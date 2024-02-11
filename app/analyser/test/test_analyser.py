import unittest
from unittest.mock import patch, MagicMock
from statistics import mean, stdev
from app.analyser.src.analyser import Analyser 

class TestAnalyser(unittest.TestCase):

    @patch('app.analyser.src.analyser.requests.get')
    def test_fetch_signals_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [1,2,3,4,5,6]

        analyser = Analyser(api_base_url='https://example.com/api')
        signals = analyser.fetch_signals()

        mock_get.assert_called_once_with('https://example.com/api/signals')
        self.assertEqual(signals, [1,2,3,4,5,6])

    @patch('app.analyser.src.analyser.requests.get')
    def test_fetch_signals_failure(self, mock_get):
        mock_get.return_value.status_code = 404

        analyser = Analyser(api_base_url='https://example.com/api')
        signals = analyser.fetch_signals()

        mock_get.assert_called_once_with('https://example.com/api/signals')
        self.assertEqual(signals, [])

    @patch('app.analyser.src.analyser.fetch_signals', return_value=[{'id': 1, 'name': 'signal1'}, {'id': 2, 'name': 'signal2'}])
    @patch('app.analyser.src.analyser.requests.get')
    def test_get_signal_by_id_success(self, mock_get, mock_fetch_signals):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'id': 1, 'name': 'signal1', 'value': 10.5}

        analyser = Analyser(api_base_url='https://example.com/api')
        signal = analyser.get_signal_by_id(1)

        mock_get.assert_called_once_with('https://example.com/api/signals/1')
        self.assertEqual(signal, {'id': 1, 'name': 'signal1', 'value': 10.5})

    @patch('app.analyser.src.analyser.Analyser.fetch_signals', return_value=[{'id': 1, 'name': 'signal1'}, {'id': 2, 'name': 'signal2'}])
    @patch('app.analyser.src.analyser.requests.get')
    def test_get_signal_by_id_failure(self, mock_get, mock_fetch_signals):
        mock_get.return_value.status_code = 404

        analyser = Analyser(api_base_url='https://example.com/api')
        signal = analyser.get_signal_by_id(1)

        mock_get.assert_called_once_with('https://example.com/api/signals/1')
        self.assertIsNone(signal)

    @patch('app.analyser.src.analyser.requests.get')
    def test_get_signal_values_iteratively_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{'value': 10.5}, {'value': 15.2}]

        analyser = Analyser(api_base_url='https://example.com/api')
        signal_values = analyser.get_signal_values_iteratively(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1)

        mock_get.assert_called_once_with('https://example.com/api/signals/1/values', params={'start': '2022-01-01', 'end': '2022-02-01', 'page_size': 10, 'offset': 0})
        self.assertEqual(signal_values, [10.5, 15.2])

    @patch('app.analyser.src.analyser.requests.get')
    def test_get_signal_values_iteratively_failure(self, mock_get):
        mock_get.return_value.status_code = 404

        analyser = Analyser(api_base_url='https://example.com/api')
        signal_values = analyser.get_signal_values_iteratively(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1)

        mock_get.assert_called_once_with('https://example.com/api/signals/1/values', params={'start': '2022-01-01', 'end': '2022-02-01', 'page_size': 10, 'offset': 0})
        self.assertEqual(signal_values, [])

    def test_calculate_statistic(self):
        analyser = Analyser(api_base_url='https://example.com/api')
        analyser.get_signal_values_iteratively = MagicMock(return_value=[10.5, 15.2, 12.3])

        result = analyser.calculate_statistic(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1, group=['group1'], statistic_function=mean)

        analyser.get_signal_values_iteratively.assert_called_once_with(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1)
        self.assertEqual(result, [{'id': 1, 'name': 'signal1', 'mean': 12.67}])

    def test_mean(self):
        analyser = Analyser(api_base_url='https://example.com/api')
        analyser.calculate_statistic = MagicMock(return_value=[{'id': 1, 'name': 'signal1', 'mean': 12.67}])

        result = analyser.mean(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1, group=['group1'])

        analyser.calculate_statistic.assert_called_once_with(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1, group=['group1'], statistic_function=mean)
        self.assertEqual(result, [{'id': 1, 'name': 'signal1', 'mean': 12.67}])

    def test_std(self):
        analyser = Analyser(api_base_url='https://example.com/api')
        analyser.calculate_statistic = MagicMock(return_value=[{'id': 1, 'name': 'signal1', 'std': 2.5}])

        result = analyser.std(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1, group=['group1'])

        analyser.calculate_statistic.assert_called_once_with(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1, group=['group1'], statistic_function=stdev)
        self.assertEqual(result, [{'id': 1, 'name': 'signal1', 'std': 2.5}])

    def test_stats(self):
        analyser = Analyser(api_base_url='https://example.com/api')
        analyser.calculate_statistic = MagicMock(return_value=[{'id': 1, 'name': 'signal1', 'mean': 12.67, 'std': 2.5}])

        result = analyser.stats(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1, group=['group1'])

        analyser.calculate_statistic.assert_called_once_with(start='2022-01-01', end='2022-02-01', page_size=10, offset=0, signal_id=1, group=['group1'], statistic_function=lambda x: (mean(x), stdev(x)))
        self.assertEqual(result, [{'id': 1, 'name': 'signal1', 'mean': 12.67, 'std': 2.5}])

    def test_raw(self):
        analyser = Analyser(api_base_url='https://example.com/api')
        analyser.get_signal_values_iteratively = MagicMock(return_value=[10.5, 15.2, 12.3])

        result = analyser.raw(start='2022-01-01', end='2022-02-01', batch_size=10, offset=0, signal_id=1)

        analyser.get_signal_values_iteratively.assert_called_once_with(start='2022-01-01', end='2022-02-01', batch_size=10, offset=0, signal_id=1)
        self.assertEqual(result, [10.5, 15.2, 12.3])

if __name__ == '__main__':
    unittest.main()
