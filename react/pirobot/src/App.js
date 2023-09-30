import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";

import './App.css';
import Home from "./home";
import PictureGallery from "./gallery"
class App extends React.Component {

    nextPath = (path) => {
        this.props.history.push(path);
    }

    render() {
        return (
        <BrowserRouter>
          <Routes>
            <Route path="/">
                <Route index element={<Home nextPath={this.nextPath}/>} />
                <Route path="pictures" element={<PictureGallery />} />
            </Route>
          </Routes>
        </BrowserRouter>
      );
    }
}

export default App;
