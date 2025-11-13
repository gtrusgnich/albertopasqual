const galleryMenuItems = () => {
    let result = '';
    $.getJSON("../assets/gallery.json", (data) => {
        data.forEach(el => {
           result += `<li><a class="dropdown-item" href="gallery.html#${el["key"]}">${el["key"]}</a></li`
        });
    })
    return result;
}