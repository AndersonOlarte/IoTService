import React, {Component} from "react";
import "./App.css"
export default class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      longitude: 0,
      latitude: 0,
      showICA: false,
      ica:0,
      aqi:0,
      contState:'',
      showWait:false,
      showManual: false
    };
}
  savePosition = (position) => {
    this.setState({
      longitude:position.coords.longitude,
      latitude: position.coords.latitude
    }
    )
    console.log(this.state.longitude)
    this.onCalculateICA()
  }
  onGetPosition = () => {
    navigator.geolocation.getCurrentPosition(this.savePosition)
  }
  onClickManual = () => {
    this.setState({showManual:true, showICA:false})

  }
  onClickForm = (e) => {
    if (e.target.name === 'send') {
      let latitude = e.target.parentNode.parentNode.childNodes[1].childNodes[1].value
      let longitude = e.target.parentNode.parentNode.childNodes[2].childNodes[1].value
      this.setState({latitude:latitude, longitude: longitude})
      this.onCalculateICA()
    }
    else {
      e.target.parentNode.parentNode.childNodes[1].childNodes[1].value = ""
      e.target.parentNode.parentNode.childNodes[2].childNodes[1].value = ""
    }
  }



  onCalculateICA = ()=> {
    this.setState({showICA: false,showWait:true, showManual:false})
    var url = 'http://localhost/requestICA'
    var data = {longitude: this.state.latitude,
                latitude: this.state.longitude}
    fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
      // mode: 'no-cors',
      headers:{
        'Content-Type': 'application/json'
      }
    }).then(res => res.json())
    .catch(error => console.error('Error:', error))
    .then(res => {
      console.log('Success:',res)
      console.log(res)
      this.setState({showICA: true, ica : res.ica,aqi: res.aqi, contState:res.state, showWait:false})
    });
  }
  render() {
    return(
      <section className = " main-container">
        <div className ="main-contanier_text">
          <h1>CONTAMINACIÓN EN EL AIRE</h1>
          <p>Pulsa en el botón medir para obtener la calidad del aire en el lugar
            donde te encuentras
          </p>
        </div>
        <div className ="main-container_elements">
          {this.state.showManual &&
            <div className = "main-container_manual">
              <p>Ingresa los datos de tu ubicación</p>
              <div className = "longitude">
                <label >Latitud</label>
                <input type="number" name="latitud" placeholder = "Latitud"/>
              </div>
              <div className = "latitude">
                <label >Longitud</label>
                <input type="number" name="longitud" placeholder = "longitud"/>
              </div>
              <div>
                <button type="button" name = "send" className = "form-button" onClick = {this.onClickForm}>Enviar</button>
                <button type="button" name = "erase"className = "form-button"onClick = {this.onClickForm}>Borrar</button>
              </div>
            </div>
          }
          {this.state.showICA &&
            <div>
              <h2>tu ubicación es la siguiente: </h2>
              <ul>
                <li>latitud = {this.state.latitude}.</li>
                <li>Longitud = {this.state.longitude}.</li>
              </ul>
              <p>El valor de la contaminación en tu ubicación es: {this.state.ica}</p>
              <p>Indice de calidad del aire: {this.state.aqi}</p>
              <p>estado de calidad del aire: {this.state.contState}</p>
            </div>
          }
          {this.state.showWait &&
            <p>Calculando la contaminación...</p>
          }
          <div className = "main-container_buttons">
            <button type="button" onClick={this.onGetPosition}> Calcular contaminación</button>
            <button type="button" onClick = {this.onClickManual}>Ubicación manual</button>
          </div>

        </div>
      </section>
    )
  }
}