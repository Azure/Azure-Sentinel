from datetime import timedelta

class TimeRangeSplitter:
    def __init__(self, min_split_time_range_after_timeout_in_seconds, max_split_time_range_chunks_after_timeout):
        self.min_split_time_range_after_timeout_in_seconds = min_split_time_range_after_timeout_in_seconds
        self.max_split_time_range_chunks_after_timeout = max_split_time_range_chunks_after_timeout

    # Function that gets a time range and splits into multiple chunks. It tries to split into max_split_time_range_chunks_after_timeout parts, assuming each intended chunk is under min_split_time_range_seconds_after_timeout. If not, it chunks into less parts.
    # Thus, a 60 seconds time range, should usually be split into 4 equal 15-seconds parts.
    def split_time_range_into_pairs(self, start_time, end_time):
        # Calculate the total difference in seconds
        total_difference = int((end_time - start_time).total_seconds())

        # Ensure minimum difference of 15 seconds
        if total_difference < self.min_split_time_range_after_timeout_in_seconds:
            return [(start_time, end_time)]  # Single pair for differences less than 15 seconds

        # Calculate minimum possible pair duration (ensuring at least 15 seconds)
        min_pair_duration = max(self.min_split_time_range_after_timeout_in_seconds, total_difference // self.max_split_time_range_chunks_after_timeout) 

        # Check if 4 pairs fit with minimum difference
        if min_pair_duration * self.max_split_time_range_chunks_after_timeout <= total_difference:
            # Create pairs with minimum duration
            time_pairs = []
            current_time = start_time
            for i in range(self.max_split_time_range_chunks_after_timeout):
                if i == self.max_split_time_range_chunks_after_timeout-1:
                    # Last pair: adjust duration to cover remaining difference
                    next_time = end_time
                else:
                    next_time = current_time + timedelta(seconds=min_pair_duration)
                time_pairs.append((current_time, next_time))
                current_time = next_time
            return time_pairs

        # Calculate maximum possible pairs (considering remaining difference)
        max_pairs = min(self.max_split_time_range_chunks_after_timeout, total_difference // min_pair_duration)

        # Create pairs with adjustments for remaining difference
        time_pairs = []
        current_time = start_time
        for i in range(max_pairs):
            if i == max_pairs - 1:
                # Last pair: adjust duration to cover remaining difference
                next_time = end_time
            else:
                next_time = current_time + timedelta(seconds=min_pair_duration)
            time_pairs.append((current_time, next_time))
            current_time = next_time

        return time_pairs