from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.transaction import Transaction
from trytond.pyson import Eval, Bool, Not
from trytond.pool import Pool, PoolMeta
import datetime

# CLASS MILEAGE
class Mileage(Workflow, ModelSQL, ModelView):
    "Employee Mileage"
    __name__ = 'employee.mileage'
    
    
    # //////////////
    #   ATTRIBUTES
    # //////////////
    
    resource = fields.Reference('Resource', selection='get_resource')
    address = fields.Many2One('party.address', 'Address', required=True)
    distance = fields.Float('Distance', required=True)
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
                'invisible': ( (Eval('state') != 'confirmed') & (Eval('state') != 'draft') ),
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
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, periods):
        pool = Pool()
        Move = pool.get('account.move')
        Line = pool.get('account.move.line')
        
        for period in periods:
            
            amount = sum([m.distance for m in period.mileage])
            if not(period.employee.price_per_km is None):
                amount *= float(period.employee.price_per_km)
                     
            # No preguntes, pero creamos un registro en 'account.move'       
            Journal = pool.get('account.journal')
            PeriodAccount = pool.get('account.period')
            Date = pool.get('ir.date')
            
            print("0: Comenzando")
            
            # Creamos un registro 'account.move.line' para 'account.move'
            line_debit = Line()
            line_debit.account = period.employee.debit
            line_debit.debit = amount
            if line_debit.account.party_required:
                line_debit.party = period.employee.party
        
            line_credit = Line()
            line_credit.account = period.employee.credit
            line_credit.credit = amount
            if line_credit.account.party_required:
                    line_credit.party = period.employee.party
           
            print("1: Lines made")
            
            # Registro de move
            journal = Journal.search(['id', '=', 1])
            company_id = Transaction().context.get('company')
            periodAccount = PeriodAccount.find(company_id, Date.today())
            
            Config = pool.get('account.configuration')
            config = Config(1)
            
            move = Move()
            move.company = period.employee.company
            move.period = periodAccount
            move.journal = journal[0] # En el futuro, reemplazar por -> config.employee_mileage_jornal
            move.date = Date().today()
            move.lines = [line_debit, line_credit]            
            print("2: Move made -> ", move.date)
        
            move.save()
    
    @classmethod
    @ModelView.button
    @Workflow.transition('cancelled')
    def cancel(cls, resources):
        pass
    
class CompanyExtend(metaclass = PoolMeta):
    __name__ = 'company.employee'
    price_per_km = fields.Float("Price per KM", required=True)
    debit = fields.Many2One('account.account', 'Debit account', required=True)
    credit = fields.Many2One('account.account', 'Credit account', required=True)
    
class MileContiguration():
    __name__ = 'account.configuration.mileage'
    employee_mileage_journal = fields.MultiValue(fields.Many2One('account.journal', 'Default Account Journal Mileage'))
