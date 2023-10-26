from trytond.pool import Pool
from . import mileage

def register():
    Pool.register(
        mileage.Mileage,
        mileage.Period,
        mileage.CompanyExtend,
        module='employee_mileage', type_='model'
    )