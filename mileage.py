from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.pool import Pool

class Mileage(ModelSQL, ModelView):
    "Employee Mileage"
    __name__ = 'employee.mileage'
    
    resource = fields.Reference('Resource', selection='get_resource')
    address = fields.Many2One('party.address', 'Address', required=True)
    distance = fields.Float('Distance', required=True)
    date = fields.Date('Date', required=True)
    description = fields.Char('Description')
    state = fields.Selection([
        ('draft', 'draft'),
        ('confirmed', 'confirmed'),
        ('posted', 'posted'),
        ('cancelled', 'cancelled'),], 'State')
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
    
    # Workflow para el state
    @classmethod
    def __setup__(cls):
        cls._transitions |= set((
            ('draft', 'confirmed'),
            ('confirmed', 'posted'),
            ('draft', 'cancelled'),
            ('confirmed', 'cancelled')
        ))
        cls._buttons.update({
            'draft': {
                'invisible': (),
                'icon': (),
                'depends': ['state']
            },
            'confirm': {
                'invisible': (),
                'icon': (),
                'depends': ['state']
            },
            'posted': {
                'invisible': (),
                'icon': (),
                'depends': ['state']
            },
            'cancel': {
                'invisible': (),
                'icon': (),
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
    @Workflow.transition('confirm')
    def draft(cls, resources):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('post')
    def draft(cls, resources):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def draft(cls, resources):
        pass
    
class Period(ModelSQL, ModelView):
    "Period"
    __name__ = 'employee.mileage.period'
    
    name = fields.Char('Name', required=True)
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    mileage = fields.One2Many('employee.mileage', 'period', 'Mileage')