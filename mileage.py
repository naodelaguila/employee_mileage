from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.transaction import Transaction
from trytond.pyson import Eval, Bool, Not
from trytond.pool import Pool, PoolMeta
from trytond.modules.currency.fields import Monetary
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)
from trytond.exceptions import UserError
from trytond.i18n import gettext
from trytond.modules.product import price_digits
import datetime

# CLASS MILEAGE
class Mileage(ModelSQL, ModelView):
    "Employee Mileage"
    __name__ = 'employee.mileage'
    # //////////////
    #   ATTRIBUTES
    # //////////////  
    resource = fields.Reference('Resource', selection='get_resource')
    address = fields.Many2One('party.address', 'Address', required=True)
    distance = fields.Integer('Distance', required=True)
    date = fields.Date('Date', required=True)
    description = fields.Char('Description')
    period = fields.Many2One('employee.period', 'Period')
    
    @staticmethod
    def default_date():
        return datetime.date.today()
    
    # Resource functions -> Puede resultar en catástrofe
    @classmethod
    def _get_resource(cls):
        'Return list for resources' # Docstring?
        return ['project.work', 'sale.opportunity'] # Modelos que podrán ser seleccionados?
    
    @classmethod
    def get_resource(cls):
        Model = Pool().get('ir.model')  # Posible error
        models = cls._get_resource()
        models = Model.search([('model', 'in', models)])
        res = [('', '')]
        for m in models:
            print(m)
            res.append((m.model, m.name))
        return res
    
    
# CLASS PERIOD
class Period(Workflow, ModelSQL, ModelView):
    "Period"
    __name__ = 'employee.period'
    
    name = fields.Char('Name', required=True)
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    mileage = fields.One2Many('employee.mileage', 'period', 'Mileage')
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('confirmed', 'CONFIRMED'),
        ('posted', 'POSTED'),
        ('cancelled', 'CANCELLED'),], 'State', readonly=True, required=True, sort=False)
   
   #Lo de creear el move en el period   
    move = fields.Many2One('account.move', 'Account Move', readonly=True)

    @staticmethod
    def default_employee():
        employee_id = Transaction().context.get('employee')
        return employee_id
    
    @staticmethod
    def default_state():
        return 'draft'
    
    # Workflow para el state
    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions |= set((
            ('draft', 'confirmed'),
            ('draft', 'cancelled'),
            ('confirmed', 'posted'),
            ('confirmed', 'cancelled'),
            ('posted', 'cancelled'),
            ('cancelled', 'draft'),
            ))
        cls._buttons.update({
            'draft': {
                'invisible': ( (Eval('state') != 'cancelled') ),
                'depends': ['state']
            },
            'confirm': {
                'invisible': ( (Eval('state') != 'draft') ),
                'depends': ['state']
            },
            'post': {
                'invisible': ( (Eval('state') != 'confirmed') ),
                'depends': ['state']
            },
            'cancel': {
                'invisible': ( (Eval('state') != 'confirmed') & (Eval('state') != 'draft') & (Eval('state') != 'posted') ),
                'depends': ['state']
            },
        })
        
    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, periods):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('confirmed')
    def confirm(cls, periods):
        pass
    
    @classmethod
    def copy(cls, periods, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('state', 'draft')
        super().copy(periods, default=default)
    
    @classmethod
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, periods):
        pool = Pool()
        Move = pool.get('account.move')
        Line = pool.get('account.move.line')
        PeriodAccount = pool.get('account.period')
        Date = pool.get('ir.date')
        Config = pool.get('account.configuration')
        config = Config(1)

        for period in periods:
            
            # Calculamos la distancia a pagar
            if period.employee.price_per_km is None:       # Revisamos que el campo indicado no sea nulo
                raise UserError(gettext('employee_mileage.msg_no_price_per_km', name=period.employee.party.name))
            amount = sum([m.distance for m in period.mileage])
            amount *= period.employee.price_per_km
            amount = round(amount, 2)
            
            # Creamos los lines para el move
            line_debit = Line()     # Para el débito
            
            if period.employee.debit_account is None:
                raise UserError(gettext('employee_mileage.msg_debit_none', name=period.employee.party.name))
                
            line_debit.account = period.employee.debit_account
            
            line_debit.debit = amount
            if line_debit.account.party_required:
                line_debit.party = period.employee.party

            line_credit = Line()    # Para el crédito
            
            if period.employee.party.account_payable_used is None:
                raise UserError(gettext('employee_mileage.msg_credit_none', name=period.employee.party.name))
            
            line_credit.account = period.employee.party.account_payable_used
            
            line_credit.credit= amount
            if line_credit.account.party_required:
                line_credit.party = period.employee.party

            # Registro de move
            company_id = Transaction().context.get('company')
            periodAccount = PeriodAccount.find(company_id, Date.today())
            
            move = Move()
            move.company = period.employee.company
            move.period = periodAccount
            move.journal = config.employee_mileage_journal
            move.date = Date().today()
            move.origin = period
            move.lines = [line_debit, line_credit]            
            # move.save()
            
            period.move = move
        cls.save(periods)
    
    @classmethod
    @ModelView.button
    @Workflow.transition('cancelled')
    def cancel(cls, periods):
        for period in periods:
            if not period.move:
                continue
            period.move = period.move.cancel()
        cls.save(periods)
            
    
class Employee(metaclass = PoolMeta):
    __name__ = 'company.employee'
    price_per_km = Monetary("Price per KM", required=True,
        digits=price_digits, currency='currency')
    debit_account = fields.Many2One('account.account', 'Debit account', required=True)
    currency = fields.Function(fields.Many2One('currency.currency', 'Currency'), 'get_currency')
    
    @classmethod
    def get_currency(cls, journals, name):
        pool = Pool()
        Company = pool.get('company.company')
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            currency_id = company.currency.id
        else:
            currency_id = None
        return dict.fromkeys([j.id for j in journals], currency_id)
    
class Move(metaclass = PoolMeta):
    __name__ = 'account.move'
    
    @classmethod
    def _get_origin(cls):
        'Return of Model names for origin References'
        return (super(Move, cls)._get_origin() + ['employee.period'])
 
    
class AccountConfiguration(metaclass = PoolMeta):
    __name__ = 'account.configuration'
    employee_mileage_journal = fields.MultiValue(fields.Many2One('account.journal', 'Default Account Journal Mileage'))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in {'employee_mileage_journal'}:
            return pool.get('account.configuration.mileage')
        return super().multivalue_model(field)


class MileageCompany(ModelSQL, CompanyValueMixin):
    "Account Configuration Mileage"
    __name__ = "account.configuration.mileage"
    employee_mileage_journal = fields.Many2One('account.journal', 'Default Account Journal Mileage', context={'company': Eval('company', -1)})
