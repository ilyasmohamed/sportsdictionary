function upvote() {
    var vote = $(this);
    var pk = vote.data('id');
    var action = vote.data('action');
    var net_votes_count = vote.next();
    var icon = vote.children(":first");

    var downvote = vote.next().next()
    var downvoteIcon = downvote.children(":first");

    $.ajax({
			type: 'POST',
			url: "/ajax/upvote/" + pk,
			dataType: 'json',
			data : {
				'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
			},
			success: function(response){
				net_votes_count.html(response.net_votes);
				icon.toggleClass("upvoted");
				vote.toggleClass("upvoted");
				vote.blur();

				downvote.removeClass("downvoted");
				downvoteIcon.removeClass("downvoted");
			},
    });
}

function downvote() {
    var vote = $(this);
    var pk = vote.data('id');
    var action = vote.data('action');
    var net_votes_count = vote.prev();
    var icon = vote.children(":first");

    var upvote = vote.prev().prev()
    var upvoteIcon = upvote.children(":first");

    $.ajax({
			type: 'POST',
			url: "/ajax/downvote/" + pk,
			dataType: 'json',
			data : {
				'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
			},
			success: function(response){
				net_votes_count.html(response.net_votes);
				icon.toggleClass("downvoted");
				vote.toggleClass("downvoted");
				vote.blur();

				upvote.removeClass("upvoted");
				upvoteIcon.removeClass("upvoted");
			},
    });
}

function deleteDefinition() {
    var deleteDefinitionButton = $(this);
    var definition = deleteDefinitionButton.closest(".infinite-item")
    var definitionPk = deleteDefinitionButton.data('definition-id');

    $("#deleteDefinitionConfirmationModal").modal()
    .on('click', '#delete', function(e) {
        $.ajax({
			type: 'POST',
			url: "/ajax/delete-definition/" + definitionPk,
			dataType: 'json',
			data : {
				'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
			},
			success: function(response){
				definition.remove();
			},
        });
    });
}


// Connecting Handlers
$(function() {
    $('[data-action="upvote"]').click(upvote);
    $('[data-action="downvote"]').click(downvote);
    $('[data-action="delete-definition"]').click(deleteDefinition);
});