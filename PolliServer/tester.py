# tester.py

from helpers.redis_json_helper import RedisJsonHelper

def main():
    # Initialize the helper
    helper = RedisJsonHelper()

    # Test filter_by_pod_id
    pod_records = helper.filter_by_pod_id(["Pod5", "Pod8"])
    print("Pod Records:", pod_records)

    # Test filter_by_location
    location_records = helper.filter_by_location("London")
    print("Location Records:", location_records)

    # Test filter_species_only
    species_records = helper.filter_species_only()
    print("Species Records:", species_records)

    # Test filter_by_L1_conf_thresh
    L1_conf_records = helper.filter_by_L1_conf_thresh(0.5)
    print("L1 Confidence Records:", L1_conf_records)

    # Test filter_by_L2_conf_thresh
    L2_conf_records = helper.filter_by_L2_conf_thresh(0.7)
    print("L2 Confidence Records:", L2_conf_records)

    # Test get_unique_values
    # If you decide to implement get_unique_values, adjust it similarly.
    # For now, I'm keeping the index_name parameter in the call for this function.
    unique_values = helper.get_unique_values(":PolliOS.engine.records.redisJsonRecord.PodRecord:index", "$.frame.podID")
    print("Unique Pod IDs:", unique_values)

if __name__ == "__main__":
    main()