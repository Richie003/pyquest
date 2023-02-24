$( document ).ready(function() {
    $('.follow-form').submit(function(e){
        e.preventDefault()

        const user_id = $(this).attr('id')
        const followText = $(`.follow-btn${user_id}`).text()
        const whiteSpace = $.trim(followText)
        var iconTag = document.getElementById('icon')

        console.log(user_id)
        console.log(whiteSpace)


        $.ajax({
            url: '/user/profile/'+ user_id + '/',
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
//                'user_id': user_id,
//                'whiteSpace': whiteSpace
            },
            success: function(response) {
                if(whiteSpace === 'Follow'){
                    $(`.follow-btn${user_id}`).text('Unfollow')
                    if (iconTag.classList.contains('bi-person-plus')){
                        iconTag.classList.remove('bi-person-plus')
                        iconTag.classList.add('bi-person-dash')
                    }
                }else{
                    $(`.follow-btn${user_id}`).text('Follow')
                     if (iconTag.classList.contains('bi-person-dash')){
                        iconTag.classList.remove('bi-person-dash')
                        iconTag.classList.add('bi-person-plus')
                    }
                }
            },
            error: function(response) {
                console.log('error', response)
            }
        })
    })
});

    function followClick(element, user_name){
        var mssgTag = document.getElementById('mssg')
        var spanTag = document.getElementById('span_text').innerHTML
        var clearSpace = spanTag.trim()
        console.log(clearSpace)
        if (clearSpace === 'Follow'){
            mssgTag.innerHTML = 'You can now see '+ user_name + ' posts'
        }else{
            mssgTag.innerHTML = 'You wont get updates from '+ user_name + ' anymore'
        }
        document.querySelector(".bg-modal2").style="display:flex!important;"
    }
    function cancelClicker(element){
        document.querySelector(".bg-modal2").style="display:none!important;"
    }
