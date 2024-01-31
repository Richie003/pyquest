const url = window.location.href
const searchForm = document.getElementById('search-form')
const searchInput = document.getElementById('search-input')
const suggestionBox = document.getElementById('suggestion-box')
const suggestionCont = document.getElementById('suggestion-cont')
const suggestionImage = document.getElementById('suggestion-img')
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;

const sendSearchData = (blog) => {
    $.ajax({
        type: 'POST',
        url: '/search/',
        data: {
            'csrfmiddlewaretoken': csrf,
            'blog': blog, 
        },
        success: (res)=> {
            // console.log(res.data)
            const data = res.data
            if (Array.isArray(data)){
                suggestionCont.innerHTML = ""
                data.forEach(blog=> {
                    suggestionCont.innerHTML += `
                    <div class="row no-gutters align-items-center px-3 my-2">
                        <div class="col mr-2">
                        <a class="text-decoration-none font-weight-bold text-dark text-uppercase mb-1" href="/blog/${blog.pk}" >${blog.title}</a>
                        <div class="h6 mb-0 font-weight-bold text-gray-800 text-muted">${blog.author}</div>
                        </div>
                        <div class="col-auto">
                            <div class="icon-circle bg-primary">
                                <i class="fas fa-search text-white"></i>
                            </div>
                        </div>
                    </div>
                    `
                })
            }else{
                if(searchInput.value.length > 0){
                    suggestionCont.innerHTML = `<h5 class="text-xs font-weight-bold text-dark text-uppercase mb-1">${data}</h5>`
                }else{
                    suggestionBox.classList.add('d-none')
                }
            }
        },
        error: (err)=> {
            console.log(err)
        }
    })
}

searchInput.addEventListener('keyup', e=>{
    console.log(e.target.value)

    if(suggestionBox.classList.contains('d-none')){
        suggestionBox.classList.remove('d-none')
    }

    sendSearchData(e.target.value)
})