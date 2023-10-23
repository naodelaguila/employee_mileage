from trytond.pool import Pool
from . import employee_mileage

def register():
    Pool.register(
        employee_mileage.EmployeeMileage,
        module='employee_mileage', type='model'
    )