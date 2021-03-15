let url_input = document.getElementById('url');
let action = document.getElementsByClassName('action')[0];
let remove = document.getElementsByClassName('remove')[0];
let contents = document.getElementsByClassName('contents')[0];
let heading = document.getElementsByClassName('heading')[0];
let del = document.getElementById('delete');
let msg_box = document.getElementsByClassName('msg')[0];
let url = null;
let pages;
let state = 'add';
const SENDTO = "../";

let id;

fetch(SENDTO + 'get_id').then(
    res => res.json()
).then(data => {
    let results = JSON.parse(data);
    id = results['id'];
    set_heading('登録済URL', heading);
    draw_links(results['url'], contents);
})

action.addEventListener('click', e => {
    if (state == 'crawl') {
        if (!(url == null)) {
            url = url.replace(/:/, ';');
            url = url.replace(/\//g, '%');
            contents.innerHTML = "ただいま探索中です。<br>しばらくお待ちください。";
            fetch(SENDTO + 'crawl/' + url).then(
                res => res.json()
            ).then(data => {
                console.log('クロール結果が帰ってきました')
                let results = JSON.parse(data)
                pages = results.urls;
                draw_links(pages, contents);
            })
        }
    } else if (state == 'add') {
        if (!(url == null)) {
            contents.innerHTML = "ただいま記事を追加しています。<br>しばらくお待ちください。";
            fetch(SENDTO + 'update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({'id': id, 'url': url,})
            }).then(
                res => res.json()
            ).then(data => {
                let results = JSON.parse(data);
                messages = results.msg;
                msg_box.innerHTML = messages;
                set_heading('登録済URL', heading);
                draw_links(results['url'], contents);
            })
        }
    }
})

remove.addEventListener('click', e => {
    fetch(SENDTO + 'remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'id': id, 'url': url})
    }).then(
        res => res.json()
    ).then(data => {
        let results = JSON.parse(data);
        messages = results.msg;
        msg_box.innerHTML = messages;
        draw_links(results['url'], contents);
    })
})

del.addEventListener('click', e => {
    fetch(SENDTO + 'delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'id': id})
    }).then(
        res => res.json()
    )
})

url_input.addEventListener('change', e => {
    url = url_input.value;
})

window.addEventListener('beforeunload', e => {
    fetch(SENDTO + 'save').then(
        res => res.json()
    )
})

let draw_links = (array, target) => {
    inner = '<ul class="page_list">\n';
    for (let link of array) {
        inner += `<li><a href="${link}" target="_blank">${link}</a></li>\n`
    }
    inner += '</ul>'
    target.innerHTML = inner;
}
let set_heading = (text, target) => {
    target.innerHTML = text;
}
