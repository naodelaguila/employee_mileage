======================
Mileage Scenario
======================

Imports::

    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, create_tax_code
    >>> import datetime

Activate modules::

    >>> config = activate_modules('employee_mileage')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = create_fiscalyear(company)
    >>> fiscalyear.click('create_period')
    >>> periods = fiscalyear.periods
    >>> period_1, period_3, period_5 = periods[0], periods[2], periods[4]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> payable = accounts['payable']
    >>> expense = accounts['expense']
    >>> tax = accounts['tax']

Create parties::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()

Create Employees::

    >>> Employee = Model.get('company.employee')
    >>> Party = Model.get('party.party')
    >>> employee_party = Party(name='Employee')
    >>> employee_party.save()
    >>> employee1 = Employee()
    >>> employee1.company = company
    >>> employee1.price_per_km = 7.7
    >>> employee1.debit_account = payable
    >>> employee1.party = employee_party
    >>> employee1.save()

Create Mileage_Period::
    >>> Period = Model.get('employee.period')
    >>> period = Period()
    >>> period.name = 'holaName'
    >>> period.employee = employee1
    >>> mileage = period.mileage.new()
    >>> mileage.distance = 4.8
    >>> mileage.address = supplier
    >>> mileage.date = datetime.date.today()
    >>> mileage.period = period
    >>> period.save()

Buttons::

    >>> period.click('confirm')
    >>> period.click('post')

    
