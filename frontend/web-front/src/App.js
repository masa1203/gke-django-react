import React, { Component } from "react";
import axios from "axios";
import "./App.css";

class App extends Component {
  state = {
    todo: [],
  };

  componentDidMount() {
    this.getTodos();
  }

  getTodos() {
    axios
      .get("https://sawakome.page/api/")
      // .get("http://localhost:8080/api/")
      .then((res) => {
        this.setState({ todo: res.data });
      })
      .catch((err) => {
        console.log(err);
      });
  }
  render() {
    return (
      <div>
        {this.state.todo.map((item) => (
          <div key={item.id}>
            <h1>{item.title}</h1>
            <p>{item.body}</p>
          </div>
        ))}
      </div>
    );
  }
}

export default App;
