import datetime
from finance_calendars import finance_calendars

yec = YahooEarningsCalendar()
# Returns the next earnings date of BOX in Unix timestamp
# print(yec.get_next_earnings_date('META'))
# 1508716800
print(finance_calendars.get_earnings_today())
print(get_earnings_by_date(date=None))