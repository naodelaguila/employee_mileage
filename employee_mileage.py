from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool

class EmployeeMileage(ModelSQL, ModelView):
    "Employee Mileage"
    __name__ = 'employee.mileage'
    
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    resource = fields.Reference('Resource', selection='get_resource')
    address = fields.Many2One('party.address', 'Address', required=True)
    distance = fields.float('Distance', required=True)
    date = fields.date('Date', required=True)
    description = fields.Char('Description')
    
    # Resource functions -> Puede resultar en catástrofe
    @classmethod
    def _get_resource(cls):
        'Return list for resources' # Docstring?
        return ['project.work', 'sale.opportunity'] # Modelos que podrán ser seleccionados?
    
    @classmethod
    def get_resource(cls):
        Model = Pool().get('employee.mileage')  # Posible error
        models = cls._get_resource()
        models = Model.search([
            ('model', 'in', models),
        ])
        return [('', '')] + [(m.model, m.name) for m in models]