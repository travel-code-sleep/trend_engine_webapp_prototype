if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside = {
    resize: function(value) {
        console.log("resizing..."); // for testing
        setTimeout(function() {
            window.dispatchEvent(new Event("resize"));
            console.log("fired resize");
        }, 500);
    return null;
    },
};

if (!window.dash_clientside) {
  window.dash_clientside = {};
}
window.dash_clientside.clientside = {
  resize: function(value) {
    console.log("resizing..."); // for testing
    setTimeout(function() {
      window.dispatchEvent(new Event("resize"));
      console.log("fired resize");
    }, 500);
    return null;
  },

  resize2: function(value1, value2) {
    console.log("resizingV2..."); // for testing
    setTimeout(function() {
       window.dispatchEvent(new Event("resize"));
       console.log("fired resizeV2");
    }, 500);
    return value2; // for testing
  }
};