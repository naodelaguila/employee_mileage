from trytond.pool import Pool
from . import mileage

def register():
    Pool.register(
        mileage.Mileage,
        mileage.Period,
        module='employee_mileage', type_='model'
    )