$(document).ready(function() {
    $(".article-body .annotation-link").on("click", function(e) {
        e.preventDefault();
        var annotation_id = $(this).data("annotation");
        $(this).toggleClass("active");
        $(".article-body .annotation[data-annotation=" + annotation_id + "]").toggleClass("active");
    });
});
