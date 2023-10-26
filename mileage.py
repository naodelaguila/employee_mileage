from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.transaction import Transaction
from trytond.pyson import Eval, Bool, Not
from trytond.pool import Pool, PoolMeta

class Mileage(Workflow, ModelSQL, ModelView):
    "Employee Mileage"
    __name__ = 'employee.mileage'
    
    resource = fields.Reference('Resource', selection='get_resource')
    address = fields.Many2One('party.address', 'Address', required=True)
    distance = fields.Float('Distance', required=True)
    date = fields.Date('Date', required=True)
    description = fields.Char('Description')
    period = fields.Many2One('employee.mileage.period', 'Period')
    
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
    
class Period(Workflow, ModelSQL, ModelView):
    "Period"
    __name__ = 'employee.mileage.period'
    
    name = fields.Char('Name', required=True)
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    mileage = fields.One2Many('employee.mileage', 'period', 'Mileage')
    state = fields.Selection([
        ('draft', 'draft'),
        ('confirmed', 'confirmed'),
        ('posted', 'posted'),
        ('cancelled', 'cancelled'),], 'State', readonly=True, required=True, sort=False)
    
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
    def draft(cls, resources):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('confirmed')
    def confirm(cls, resources):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, resources):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('cancelled')
    def cancel(cls, resources):
        pass
    
class CompanyExtend(metaclass = PoolMeta):
    __name__ = 'company.employee'
    price_per_km = fields.Char("Price per KM")