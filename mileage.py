from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool

class Mileage(ModelSQL, ModelView):
    "Employee Mileage"
    __name__ = 'employee.mileage'
    
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    resource = fields.Reference('Resource', selection='get_resource')
    address = fields.Many2One('party.address', 'Address', required=True)
    distance = fields.Float('Distance', required=True)
    price_per_km = fields.Numeric('Price per km')
    date = fields.Date('Date', required=True)
    description = fields.Char('Description')
    state = fields.Selection([('a', 'draft'), ('b', 'confirmed'), ('c', 'posted'), ('d', 'cancelled'),], 'State')
    
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
    
class Period(ModelSQL, ModelView):
    "Period"
    __name__ = 'employee.mileage.period'
    
    name = fields.Char('Name', required=True)
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    mileage = fields.One2Many('employee.mileage', 'distance', 'Mileage', required=True)