function summonOneko() {
  document.cookie =
    "summonOneko=true; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/";
  location.reload();
}

function withdrawOneko() {
  document.cookie =
    "summonOneko=false; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/";
  location.reload();
}

function harlemShakeAndBake() {
  function c() {
    var e = document.createElement("link");
    e.setAttribute("type", "text/css");
    e.setAttribute("rel", "stylesheet");
    e.setAttribute("href", f);
    e.setAttribute("class", l);
    document.body.appendChild(e);
  }
  function h() {
    var e = document.getElementsByClassName(l);
    for (var t = 0; t < e.length; t++) {
      document.body.removeChild(e[t]);
    }
  }
  function p() {
    var e = document.createElement("div");
    e.setAttribute("class", a);
    document.body.appendChild(e);
    setTimeout(function () {
      document.body.removeChild(e);
    }, 100);
  }
  function d(e) {
    return {
      height: e.offsetHeight,
      width: e.offsetWidth,
    };
  }
  function v(i) {
    var s = d(i);
    return s.height > e && s.height < n && s.width > t && s.width < r;
  }
  function m(e) {
    var t = e;
    var n = 0;
    while (!!t) {
      n += t.offsetTop;
      t = t.offsetParent;
    }
    return n;
  }
  function g() {
    var e = document.documentElement;
    if (!!window.innerWidth) {
      return window.innerHeight;
    } else if (e && !isNaN(e.clientHeight)) {
      return e.clientHeight;
    }
    return 0;
  }
  function y() {
    if (window.scrollY) {
      return window.scrollY;
    }
    return Math.max(
      document.documentElement.scrollTop,
      document.body.scrollTop
    );
  }
  function E(e) {
    var t = m(e);
    return t >= w && t <= b + w;
  }
  function S() {
    var e = document.createElement("audio");
    e.setAttribute("class", l);
    e.src = i;
    e.loop = false;
    e.addEventListener(
      "canplay",
      function () {
        setTimeout(function () {
          x(k);
        }, 500);
        setTimeout(function () {
          N();
          p();
          for (var e = 0; e < O.length; e++) {
            T(O[e]);
          }
        }, 15500);
      },
      true
    );
    e.addEventListener(
      "ended",
      function () {
        N();
        h();
      },
      true
    );
    e.innerHTML =
      " <p>If you are reading this, it is because your browser does not support the audio element. I recommend that you get a new browser.</p> <p>";
    document.body.appendChild(e);
    e.play();
  }
  function x(e) {
    e.className += " " + s + " " + o;
  }
  function T(e) {
    e.className += " " + s + " " + u[Math.floor(Math.random() * u.length)];
  }
  function N() {
    var e = document.getElementsByClassName(s);
    var t = new RegExp("\\b" + s + "\\b");
    for (var n = 0; n < e.length; ) {
      e[n].className = e[n].className.replace(t, "");
    }
  }
  var e = 30;
  var t = 30;
  var n = 350;
  var r = 350;
  var i = "/static/audio/spells/harlem-shake.mp3";
  var s = "mw-harlem_shake_me";
  var o = "im_first";
  var u = ["im_drunk", "im_baked", "im_trippin", "im_blown"];
  var a = "mw-strobe_light";
  var f = "/static/css/harlem-shake.css";
  var l = "mw_added_css";
  var b = g();
  var w = y();
  var C = document.getElementsByTagName("*");
  var k = null;
  for (var L = 0; L < C.length; L++) {
    var A = C[L];
    if (v(A)) {
      if (E(A)) {
        k = A;
        break;
      }
    }
  }
  if (A === null) {
    console.warn(
      "Could not find a node of the right size. Please try a different page."
    );
    return;
  }
  c();
  S();
  var O = [];
  for (var L = 0; L < C.length; L++) {
    var A = C[L];
    if (v(A)) {
      O.push(A);
    }
  }
}

function dvd() {
  let x = 0,
    y = 0,
    dirX = 1,
    dirY = 1;
  const speed = 2;
  const pallete = ["#ff8800", "#e124ff", "#6a19ff", "#ff2188"];
  let dvd = document.getElementById("dvd");
  dvd.style.backgroundColor = pallete[0];
  let prevColorChoiceIndex = 0;
  let black = document.getElementById("black");
  black.style.display = "block";
  const dvdWidth = dvd.clientWidth;
  const dvdHeight = dvd.clientHeight;

  function getNewRandomColor() {
    const currentPallete = [...pallete];
    currentPallete.splice(prevColorChoiceIndex, 1);
    const colorChoiceIndex = Math.floor(Math.random() * currentPallete.length);
    prevColorChoiceIndex =
      colorChoiceIndex < prevColorChoiceIndex
        ? colorChoiceIndex
        : colorChoiceIndex + 1;
    const colorChoice = currentPallete[colorChoiceIndex];
    return colorChoice;
  }
  function animate() {
    const screenHeight = $(window).height();
    const screenWidth = document.body.clientWidth;

    if (y + dvdHeight >= screenHeight || y < 0) {
      dirY *= -1;
      dvd.style.backgroundColor = getNewRandomColor();
    }
    if (x + dvdWidth >= screenWidth || x < 0) {
      dirX *= -1;

      dvd.style.backgroundColor = getNewRandomColor();
    }
    x += dirX * speed;
    y += dirY * speed;
    dvd.style.left = x + "px";
    dvd.style.top = y + "px";
    window.requestAnimationFrame(animate);
  }

  window.requestAnimationFrame(animate);
}

function handleDVD() {
  if ($("#black").css("display") === "none") {
    dvd();
  } else {
    $("#black").css("display", "none");
  }
}
