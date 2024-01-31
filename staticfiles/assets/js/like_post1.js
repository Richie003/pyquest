$( document ).ready(function() {
    $('.like-form').submit(function(e){
        e.preventDefault()

        const blog_id = $(this).attr('id')
        const likeText = $(`.like-btn${blog_id}`).attr('data-text')
        const whiteSpace = $.trim(likeText)
        const url = $(this).attr('action')
        var iconTag = document.getElementById('icon')
        console.log(likeText)

        let res;
        const likes = $(`.like-count${blog_id}`).text()
        const str_To_int = parseInt(likes)

        $.ajax({
            url: url,
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'blog_id': blog_id,
                'whiteSpace': whiteSpace
            },
            success: function(response) {
                $(`.like-btn${blog_id}`).empty();
                if(whiteSpace === 'Liked'){
                    $(`.like-btn${blog_id}`).append('<i class="bi bi-heart"></i>')
                    res = str_To_int - 1
                }else{
                    $(`.like-btn${blog_id}`).append('<i class="bi bi-heart-fill" style="color: red !important;"></i>')
                    res = str_To_int + 1
                }
                $(`.like-count${blog_id}`).text(res)
            },
            error: function(response) {
                console.log('error', response)
            }
        })
    })
});

$('.link-btn').click(function(){
    copyToClipboard($(this).attr('data-link'))
})

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
    .then(() => {
        console.log('Text copied to clipboard: ', text);
    })
    .catch(err => {
        console.error('Unable to copy text to clipboard: ', err);
    });
}