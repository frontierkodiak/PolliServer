# tester.py

from helpers.redis_json_helper import RedisJsonHelper
from constants import *

def main():
    # Initialize the helper
    helper = RedisJsonHelper()
    
    # Test filter_pods_by_pod_name ✅
    pod_records = helper.filter_podrecords_by_pod_name("Pod11")
    print("name == Pod11 (PodRecord):", pod_records)
    
    # Test filter_specimenrecords_by_podID ✅
    specimen_records = helper.filter_specimenrecords_by_podID("Pod11")
    print("podID == Pod11 (SpecimenRecords):", specimen_records)

    # Test filter_frames_by_pod_id ❗
    frame_records = helper.filter_framerecords_by_pod_id("Pod11")
    print("Pod11 (FrameRecord):", frame_records)

    # Test filter_frames_by_location ❔
    location_records = helper.filter_framerecords_by_location("suet")
    print("Location Records:", location_records)

    # Test filter_specimens_by_taxonRank ✅
    species_records = helper.filter_specimens_by_S2_taxonRank("L10")
    print("S2_taxonRank == L10 (specimenRecord):", species_records)

    # Test filter_specimens_by_S1_score ✅
    S1_conf_records = helper.filter_specimenrecords_by_S1_score(0.1)
    print("S1 Confidence Records:", S1_conf_records)

    # Test filter_specimens_by_S2_taxonID_score ✅
    S2_conf_records = helper.filter_specimenrecords_by_S2_taxonID_score(0.2)
    print("S2 Confidence Records:", S2_conf_records)

    # # Test get_unique_pod_names_podrecord ✅
    unique_pod_names = helper.get_unique_values(PodRecord_index, 'name')
    print(f"Unique Pod Names (PodRecord): {unique_pod_names}")
    
    # Test get_unique_podIDs_framerecord
    unique_podIDs = helper.get_unique_values(FrameRecord_index, 'podID')
    print(f"Unique Pod IDs (FrameRecord): {unique_podIDs}")
    
    # Test get_unique_podIDs_specimenrecord ✅
    unique_podIDs = helper.get_unique_values(SpecimenRecord_index, 'podID')
    print(f"Unique Pod IDs (SpecimenRecord): {unique_podIDs}")

if __name__ == "__main__":
    main()