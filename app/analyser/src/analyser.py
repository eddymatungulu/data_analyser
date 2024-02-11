import requests
from statistics import mean, stdev

class Analyser:

    def __init__(self, api_base_url) -> None:
        """
        Initializes the Analyser with the provided API base URL and fetches signals.
        """
        self.api_base_url = api_base_url
        self.signals = self.fetch_signals()

    def fetch_signals(self):
        """
        Fetches signals from the API and returns the list of signals.
        """
        endpoint = f"{self.api_base_url}/signals"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch signals ID. Status code: {response.status_code}")
            return []

    def get_signal_by_id(self, signal_id) -> object:
        """
        Fetches a signal by its ID from the API.
        """
        endpoint = f"{self.api_base_url}/signals/{signal_id}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch signal with ID {signal_id}. Status code: {response.status_code}")
            return None

    def get_signal_values_iteratively(self, start, end, page_size, offset, signal_id) -> object:
        """
        Fetches signal values iteratively based on the specified parameters.
        """
        signal_values = []
        current_offset = offset

        while True:
            endpoint = f"{self.api_base_url}/signals/{signal_id}/values"
            params = {'start': start, 'end': end, 'page_size': page_size, 'offset': current_offset}
            response = requests.get(endpoint, params=params)

            if response.status_code == 200:
                results = response.json()
                if not results:
                    break  # No more values to fetch

                # Extracting values from the results and extending the list
                signal_values.extend(item['value'] for item in results)
                current_offset += page_size
            else:
                print(f"Failed to fetch signal values. Status code: {response.status_code}")
                break

        return signal_values

    def calculate_statistic(self, start, end, page_size, offset, signal_id, group=None, statistic_function=None):
        """
        Calculates a specified statistic for signals based on the specified parameters.
        """
        result_values_by_name = []

        for signal in self.signals:
            signal_id = signal['id']
            signal_name = signal['name']
            signal_group = signal['group']

            if group and not any(element in group for element in signal_group):
                continue  # Skip if the signal does not belong to the specified group

            signal_values = self.get_signal_values_iteratively(start, end, page_size, offset, signal_id)

            if signal_values:
                statistic_value = statistic_function(signal_values)
                result_values_by_name.append({'id': signal_id, 'name': signal_name, statistic_function.__name__: statistic_value})

        return result_values_by_name

    def mean(self, start, end, page_size, offset, signal_id, group=None) -> object:
        """
        Calculates the mean for signals based on the specified parameters.
        """
        return self.calculate_statistic(start, end, page_size, offset, signal_id, group, mean)

    def std(self, start, end, page_size, offset, signal_id, group=None) -> object:
        """
        Calculates the standard deviation for signals based on the specified parameters.
        """
        return self.calculate_statistic(start, end, page_size, offset, signal_id, group, stdev)

    def stats(self, start, end, page_size, offset, signal_id, group=None) -> object:
        """
        Calculates both mean and standard deviation for signals based on the specified parameters.
        """
        return self.calculate_statistic(start, end, page_size, offset, signal_id, group, lambda x: (mean(x), stdev(x)))

    def raw(self, start, end, batch_size, offset, signal_id) -> object:
        """
        Fetches raw signal values based on the specified parameters.
        """
        return self.get_signal_values_iteratively(start, end, batch_size, offset, signal_id)
