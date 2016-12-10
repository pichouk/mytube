function showVideo(video_id){
  var frame = document.createElement('iframe');
  frame.setAttribute('src','https://www.youtube.com/embed/'+video_id);
  frame.setAttribute('class','embed-responsive_item');
  frame.setAttribute('allowfullscreen','');

  var div_container = document.getElementById('video_frame')
  div_container.replaceChild(frame,div_container.firstChild);
}
