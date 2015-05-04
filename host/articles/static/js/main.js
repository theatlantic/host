(function() {
    $(".annotation-link").on("click", function(e) {
        e.preventDefault();
        var annotation_id = $(this).data("annotation");
        $(".annotation[data-annotation=" + annotation_id + "]").toggleClass("active");
    });

    var touchStart = {x: 0, y: 0, time: 0};
    var touchDelta = {x: 0, y: 0, time: 0};
    $(document).on("touchstart", function(e) {
        var touch = e.originalEvent.touches[0];

        touchStart = {
            x: touch.pageX,
            y: touch.pageY,
            time: +(new Date())
        };
    });

    $(document).on("touchmove", function(e) {
        var touch = e.originalEvent.touches[0];
        touchDelta.x = touchStart.x - touch.pageX;
        touchDelta.y = touchStart.y - touch.pageY;
    });

    $(document).on("touchend", function(e) {
        var elem = document.elementFromPoint(touchStart.x, touchStart.y);
        touchDelta.time = +(new Date()) - touchStart.time;

        if (touchDelta.time < 250 && Math.sqrt((touchDelta.x * touchDelta.x) + (touchDelta.y * touchDelta.y)) < 10) {
            $(elem).trigger("tap");
        }

        touchStart = {x: 0, y: 0, time: 0};
        touchDelta = {x: 0, y: 0, time: 0};
    });

    $(".annotation").on("tap", function(e) {
        if (e.target != this) { return; }
        if ($(this).hasClass("active")) {
            $(this).toggleClass("active");
        }
    });
})();
