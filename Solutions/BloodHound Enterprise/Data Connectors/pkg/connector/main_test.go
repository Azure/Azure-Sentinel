package connector

import (
	"encoding/json"
	"testing"
	"time"

	. "function/pkg/model"

)

// Testing some time formatting here
func TestTimeFormatting(testing *testing.T) {
	t := time.Now()
	var s = t.Format("2006-01-02T15:04:05.000Z")
	testing.Logf("Explicit format %s\n", s)
	s = t.Format(time.RFC3339Nano)
	testing.Logf("RFC3339Nano format %s\n", s)
	s = t.UTC().Format(time.RFC3339Nano)
	testing.Logf("UTC RFC3339Nano format %s\n", s)
	testing.Fatalf("")
}

func TestCreateBatches(t *testing.T) {
	testRecord := BloodhoundEnterpriseData{
		EventType:    "a;lksdjfa;lskdjf;alskdjf;alsdkjf;alsdkjf;alskdjf;alskdjfa;lsdkjf;alskjdfalskjdfalksdjf",
		EventDetails: "a;lskdfja;sldkfja;sldkfja;sldkfja;lsdkjfa;sldkfja;lsdkjfa;lsdkjfa;lskdjfalskdfjaldkjf",
	}
	var testRecords = make([]BloodhoundEnterpriseData, 50000)
	for i := range 50000 {
		testRecords[i] = testRecord
	}

	jsonRecords, _ := json.Marshal(testRecords)
	t.Logf("size of record list %d", len(jsonRecords))

	batches, err := CreateBatches(testRecords, 1000000)
	if err != nil {
		t.Fatalf("Error creating batches %v", err)
	}
	var c = 0
	for _, batch := range batches {
		c += len(batch)
	}
	if c != len(testRecords) {
		t.Fatalf("Size of batches %d", len(batches))
		t.Fail()
	}
	type args struct {
		records       []BloodhoundEnterpriseData
		maxUploadSize int64
	}
	if false {
		t.Fail()
	}
}

func TestPop(t *testing.T) {
	testRecord := BloodhoundEnterpriseData{
		EventType:    "a;lksdjfa;lskdjf;alskdjf;alsdkjf;alsdkjf;alskdjf;alskdjfa;lsdkjf;alskjdfalskjdfalksdjf",
		EventDetails: "a;lskdfja;sldkfja;sldkfja;sldkfja;lsdkjfa;sldkfja;lsdkjfa;lsdkjfa;lskdjfalskdfjaldkjf",
	}
	var testRecords = make([]BloodhoundEnterpriseData, 50000)
	for i := range 50000 {
		testRecords[i] = testRecord
	}

	jsonRecords, _ := json.Marshal(testRecords)
	t.Logf("size of record list %d", len(jsonRecords))

	var batchesToMarshal, _ = CreateBatches(testRecords, 1000000)
	originalLength := len(batchesToMarshal)

	// var batch = make([]BloodhoundEnterpriseData, 1)
	batch, batchesToMarshal := batchesToMarshal[len(batchesToMarshal)-1], batchesToMarshal[:len(batchesToMarshal)-1]

	if len(batchesToMarshal) != originalLength - 1 {
		t.Fatalf("Batch size not reduced after pop orig: %d new: %d", originalLength, len(batchesToMarshal))
	}
	if batch[0].ID != 0 {
		t.Fatalf("First batch should be 0, %d", batch[0].ID)
	}

	batchJSON, err := json.Marshal(batch)
	if err != nil {
		t.Fatal()
	}
	if len(batchJSON) > 1000000 {
		t.Fatal()
	}

}

func TestCreateBatchesGauranteed(t *testing.T) {
	testRecord := BloodhoundEnterpriseData{
		EventType:    "a;lksdjfa;lskdjf;alskdjf;alsdkjf;alsdkjf;alskdjf;alskdjfa;lsdkjf;alskjdfalskjdfalksdjf",
		EventDetails: "a;lskdfja;sldkfja;sldkfja;sldkfja;lsdkjfa;sldkfja;lsdkjfa;lsdkjfa;lskdjfalskdfjaldkjf",
	}
	var testRecords = make([]BloodhoundEnterpriseData, 50000)
	for i := range 50000 {
		testRecords[i] = testRecord
	}

	jsonRecords, _ := json.Marshal(testRecords)
	t.Logf("size of record list %d", len(jsonRecords))

	possibleBatchesToMarshal, err := CreateBatches(testRecords, 1000000)
	if err != nil {
		t.Fatal()
	}

	numApproxSizedBatches := len(possibleBatchesToMarshal)
	if err != nil {
		t.Fatal()
	}
	batchesToMarshal, err := CreateBatchesGauranteedToFit(testRecords, 1000000)
	numGauranteedBatches := len(batchesToMarshal)
	if err != nil {
		t.Fatal()
	}

		// These numbers might not match if the approximate batch sizes creted by CreateBatchs are a little too big
		// they will be split by CreateBatchesGauranteedToFit
	if numApproxSizedBatches != numGauranteedBatches {
		t.Logf("num approx: %d num gauranteed: %d", numApproxSizedBatches, numGauranteedBatches)
	}

	var c = 0
	for _, b := range batchesToMarshal {
		testRecords := make([]BloodhoundEnterpriseData, 0)
		json.Unmarshal(b, &testRecords)
		c += len(testRecords)
	}

	if c != len(testRecords) {
		t.Logf("unmarshaled num records %d original num records %d", c, len(testRecords))
		t.Fatal()
	}

	if len(batchesToMarshal) == 0 {
		t.Fatal()
	}

}

func TestRecordsTooBig(t *testing.T) {
	testRecord := BloodhoundEnterpriseData{
		EventType:    "a;lksdjfa;lskdjf;alskdjf;alsdkjf;alsdkjf;alskdjf;alskdjfa;lsdkjf;alskjdfalskjdfalksdjf",
		EventDetails: "a;lskdfja;sldkfja;sldkfja;sldkfja;lsdkjfa;sldkfja;lsdkjfa;lsdkjfa;lskdjfalskdfjaldkjf",
	}
	var testRecords = make([]BloodhoundEnterpriseData, 50000)
	for i := range 50000 {
		testRecords[i] = testRecord
	}

	singleRecordSize, _ := json.Marshal(testRecords[0])

	maxRecordSize := int64(10)
	_, err := CreateBatches(testRecords, maxRecordSize)
	if err == nil {
		t.Logf("Error creating batches should fail when single record size %d will not fit max record size %d", singleRecordSize, maxRecordSize)
	}

	_, anerr := CreateBatchesGauranteedToFit(testRecords, maxRecordSize)
	if anerr == nil {
		t.Logf("Error creating gauranteed batches should fail when single record size %d will not fit max record size %d", singleRecordSize, maxRecordSize)
	}

	if err == nil || anerr == nil {
		t.Fatal()
	}
}
