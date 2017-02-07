window.onload = function() {
    var baseUrl = 'http://irvm-samridh:5000/';
    var data = {
        name: 'Buckets'
    };
    $.get(baseUrl + 'buckets?limit=5')
        .done(function(buckets) {
            data.children = buckets;
            var folderPromises = buckets.map(function(bucket) {
                return $.get(baseUrl + 'buckets/' + bucket.name + '/folders');
            });
            $.when(...folderPromises)
                .done(function(...folderArrays) {
                    folderArrays.forEach(function(folders, index) {
                        data.children[index].children = folders[0];
                    });
                    renderData(data);
                });
        });
    var svg = d3.select("svg"),
    margin = 20,
    diameter = +svg.attr("width"),
    g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(50, 100%, 53%)", "hsl(0, 100%, 56%)"])
        .interpolate(d3.interpolateHcl);

    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    function renderData(root) {

        root = d3.hierarchy(root)
            .sum(function(d) { return d.size; })
            .sort(function(a, b) { return b.value - a.value; });

        var focus = root,
            nodes = pack(root).descendants(),
            view;

        var circle = g.selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
            .style("fill", function(d) { return d.children ? color(d.depth) : null; })
            .on("click", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); });

        var text = g.selectAll("text")
            .data(nodes)
            .enter().append("text")
            .attr("class", "label")
            .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
            .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
            .text(function(d) {
                var parts = d.data.name.split('/');
                return parts[parts.length - 1] + ' ' + formatSize(d.data.size) + ' ' + '~$' + formatPrice(d.data.size) + ' per month.' ;
            });

        var node = g.selectAll("circle,text");

        svg
            .style("background", color(-1))
            .on("click", function() { zoom(root); });

        zoomTo([root.x, root.y, root.r * 2 + margin]);

        function zoom(d) {
            var focus0 = focus; focus = d;

            var transition = d3.transition()
                .duration(d3.event.altKey ? 7500 : 750)
                .tween("zoom", function(d) {
                    var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
                    return function(t) { zoomTo(i(t)); };
                });

            transition.selectAll("text")
            .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
                .style("fill-opacity", function(d) { return d.parent === focus ? 1 : 0; })
                .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
                .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });
        }

        function zoomTo(v) {
            var k = diameter / v[2]; view = v;
            node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
            circle.attr("r", function(d) { return d.r * k; });
        }
    };

    function formatPrice(value) {
        value = value / 1e9;
        return Math.round(value * 0.021);
    }

    function formatSize(value) {
        value = +value;
        base = 1024;
        var units = ['B', 'K', 'M', 'G', 'T', 'P'];
        var index = 0, len = units.length - 1;
        while (value / base >= 1 && index < len) {
            value /= base;
            index++;
        }
        return value.toFixed(2) + ' ' + units[index];
    }
};
