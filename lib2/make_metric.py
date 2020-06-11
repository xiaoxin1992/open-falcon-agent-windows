class Metric:
    def make_data(self, metric, value, c_type="", tags="", timestamp=0):
        return {
            "endpoint": self.hostname,
            "metric": metric,
            "timestamp": timestamp,
            "step": self.push_interval,
            "value": value,
            "counterType": c_type,
            "tags": tags
        }
