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
            move = Move()
            periodMove = pool.get('account.period')
            journalMove = pool.get('account.journal')
            Date = pool.get('ir.date')
            
            periodAccount = periodMove()
            periodAccount.end_date = Date().today()
            periodAccount.save()
            
            move.date = Date().today()
            move.company = period.employee.company
            move.period = periodAccount
            move.journal = journalMove().save()
            
            # Creamos un registro 'account.move.line' para 'account.move'
            lineDebit = Line()
            lineDebit.account = period.employee.debit
            lineDebit.debit = amount
            lineDebit.party = period.employee.party
            lineDebit.save()
            
            lineCredit = Line()
            lineCredit.account = period.employee.credit
            lineCredit.credit = amount
            lineCredit.party = period.employee.party
            lineCredit.save()
        
            move.lines = [lineDebit, lineCredit]
            move.save()

            
        
         
    
    @classmethod
    @ModelView.button
    @Workflow.transition('cancelled')
    def cancel(cls, resources):
        pass
    
class CompanyExtend(metaclass = PoolMeta):
    __name__ = 'company.employee'
    price_per_km = fields.Float("Price per KM")
    debit = fields.Many2One('account.account', 'Debit account')
    credit = fields.Many2One('account.account', 'Credit account')
   