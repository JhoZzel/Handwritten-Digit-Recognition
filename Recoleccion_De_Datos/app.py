import tempfile
import os
from flask import Flask, render_template_string, request, redirect, send_file
from skimage import io
import base64
import glob
import numpy as np

app = Flask(__name__)

main_html = """
<html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

   function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
   }

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");


      numero = getRndInteger(0, 20);
      letra = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
      random = Math.floor(Math.random() * letra.length);
      aleatorio = letra[random];

      document.getElementById('mensaje').innerHTML  = 'Dibujando un ' + aleatorio;
      document.getElementById('numero').value = aleatorio;

      $('#myCanvas').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas').mouseup(function (e) {
          mousePressed = false;
      });
  	    $('#myCanvas').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      // Use the identity matrix while clearing the canvas
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  //https://www.askingbox.com/tutorial/send-html5-canvas-as-image-to-server
  function prepareImg() {
     var canvas = document.getElementById('myCanvas');
     document.getElementById('myImage').value = canvas.toDataURL();
  }



</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" ></script>
    <div align="left">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/Uni-logo_transparente_granate.png" width="300"/>
    </div>
    <div align="center">
        <h1 id="mensaje">Dibujando...</h1>
        <canvas id="myCanvas" width="200" height="200" style="border:2px solid black"></canvas>
        <br/>
        <br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>
    <div align="center">
      <form method="post" action="upload" onsubmit="javascript:prepareImg();"  enctype="multipart/form-data">
      <input id="numero" name="numero" type="hidden" value="">
      <input id="myImage" name="myImage" type="hidden" value="">
      <input id="bt_upload" type="submit" value="Enviar">
      </form>
    </div>
    <div align="center">
      <form method="get" action="prepare">
      <input id="bt_prepare" type="submit" value="Preparar">
      </form>
    </div>
</body>
</html>

"""

@app.route("/")
def main():
    return(main_html)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # check if the post request has the file part
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        aleatorio = request.form.get('numero')
        print(aleatorio)
        with tempfile.NamedTemporaryFile(delete = False, mode = "w+b", suffix='.png', dir=str(aleatorio)) as fh:
            fh.write(base64.b64decode(img_data))
        #file = request.files['myImage']
        print("Image uploaded")
    except Exception as err:
        print("Error occurred")
        print(err)

    return redirect("/", code=302)


@app.route('/prepare', methods=['GET'])
def prepare_dataset():
    images = []
    d = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    digits = []
    for digit in d:
      filelist = glob.glob('{}/*.png'.format(digit))
      images_read = io.concatenate_images(io.imread_collection(filelist))
      images_read = images_read[:, :, :, 3]
      digits_read = np.array([digit] * images_read.shape[0])
      images.append(images_read)
      digits.append(digits_read)
    images = np.vstack(images)  
    digits = np.concatenate(digits)
    np.save('X.npy', images)
    np.save('Y.npy', digits)

    ok_script = """
    <script>
        // Función para añadir un div "OK" a la página actual
        function addOkDiv() {
            var okDiv = document.createElement('div');
            okDiv.textContent = 'OK, Presiona "Enviar" para agregar mas datos';
            okDiv.style.textAlign = 'center';  // Centrar horizontalmente el texto
            okDiv.style.margin = '0 auto';     // Centrar horizontalmente el contenedor div
            document.body.appendChild(okDiv);
        }

        // Llamar a la función para añadir el div "OK" al cargar la página
        window.onload = addOkDiv;
    </script>
    """

    return render_template_string(main_html + ok_script)

@app.route('/X.npy', methods=['GET'])
def download_X():
    return send_file('./X.npy')
@app.route('/Y.npy', methods=['GET'])
def download_y():
    return send_file('./Y.npy')

if __name__ == "__main__":
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    for d in digits:
        if not os.path.exists(str(d)):
            os.mkdir(str(d))
    app.run()