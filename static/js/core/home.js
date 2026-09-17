const announcementsMarquee = document.getElementById('announcementsMarquee')
const marquee = new Marquee(announcementsMarquee, {
    behavior: 'scroll',
    direction: 'up',
    scrollamount: 1,
    scrolldelay: 50,
    width: '100%',
    height: '236px',
    onmouseover: 'this.stop()',
    onmouseout: 'this.start()'
})