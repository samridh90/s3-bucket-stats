window.onload = function() {
	var onBucketsFetch = function (buckets) {
        console.log(buckets);
    };
	d3.json("/buckets", onBucketsFetch);
};

