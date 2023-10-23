from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool

class EmployeeMileage(ModelSQL, ModelView):
    "Employee Mileage"
    __name__ = 'employee_mileage'
    
    