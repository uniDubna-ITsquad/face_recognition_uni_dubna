from datetime import datetime, timedelta, date

class TimeGenerator:
    def __init__(self, interval_ms, start_time = None):
        self.interval_ms = interval_ms
        tmp_date = date.today()
        if start_time == None:
            self._start_date = datetime(
                tmp_date.year, tmp_date.month, tmp_date.day
            )
        else:
            self._start_date = start_time
        self._counter = 0

    def next(self):
        t_delta = timedelta(minutes = self._counter * self.interval_ms / 60 / 1000)
        self._counter += 1
        return self._start_date + t_delta

    def get_count(self):
        return self._counter