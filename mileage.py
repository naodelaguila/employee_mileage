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
    period = fields.Many2One('employee.mileage.period', 'Period')
    
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
    __name__ = 'employee.mileage.period'
    
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
            print(period.mileage)
            
            km = sum([m.distance for m in period.mileage])
            amount = km * period.employee.price_per_km
            
            move = Move()
            period = move.period
            move.effective_date = period.effective_date
            move.journal = period.joural
            move.lines = period.lines
            
            line = Line()
            line.account = period.employee.debit
            line.debit = amount
            line.move = move
            
            line.party = period.employee.party
            line.account = period.employee.credit
            line.credit = amount
            
        
         
    
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
   