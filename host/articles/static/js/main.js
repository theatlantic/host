(function() {
    $(".annotation-link").on("click", function(e) {
        e.preventDefault();
        var annotation_id = $(this).data("annotation");
        $(".annotation[data-annotation=" + annotation_id + "]").toggleClass("active");
    });
})();
