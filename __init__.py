from trytond.pool import Pool
from . import mileage

def register():
    Pool.register(
        mileage.Mileage,
        module='employee_mileage', type_='model'
    )