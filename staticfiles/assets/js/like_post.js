$( document ).ready(function() {
    $('.like-form').submit(function(e){
        e.preventDefault()

        const blog_id = $(this).attr('id')
        const likeText = $(`.like-btn${blog_id}`).text()
        const whiteSpace = $.trim(likeText)
        const url = $(this).attr('action')
        var iconTag = document.getElementById('icon')
        console.log(url)

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
                if(whiteSpace === 'Liked'){
                    $(`.like-btn${blog_id}`).text('Like')
                    res = str_To_int - 1
                }else{
                    $(`.like-btn${blog_id}`).text('Liked')
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