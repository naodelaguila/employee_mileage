======================
MIleage Scenario
======================

Imports::

    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, create_tax_code

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


Create a moves::

    >>> Journal = Model.get('account.journal')
    >>> Move = Model.get('account.move')
    >>> journal_revenue, = Journal.find([
    ...         ('code', '=', 'REV'),
    ...         ])
    >>> journal_cash, = Journal.find([
    ...         ('code', '=', 'CASH'),
    ...         ])
    >>> move = Move()
    >>> move.period = period_3
    >>> move.journal = journal_revenue
    >>> move.date = period_3.start_date
    >>> line = move.lines.new()
    >>> line.account = child_revenue
    >>> line.credit = Decimal(10)
    >>> line = move.lines.new()
    >>> line.account = receivable
    >>> line.debit = Decimal(10)
    >>> line.party = party
    >>> move.save()

    >>> move = Move()
    >>> move.period = period_5
    >>> move.journal = journal_cash
    >>> move.date = period_5.start_date
    >>> line = move.lines.new()
    >>> line.account = cash
    >>> line.debit = Decimal(10)
    >>> line = move.lines.new()
    >>> line.account = receivable
    >>> line.credit = Decimal(10)
    >>> line.party = party
    >>> move.save()