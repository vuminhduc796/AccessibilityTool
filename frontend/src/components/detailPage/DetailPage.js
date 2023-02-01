import React from 'react'
import { useContext } from 'react';
import { Row, Col } from "react-bootstrap";
import { useState } from "react";
import { AppContext } from '../../context/Context';
import "./DetailPage.css";

const DetailPage = () => {

  var data = useContext(AppContext);
  var [node, setNode] = data["currentNode"]

  const [google_report, setData] = useState("")
  const [uichecker, setUichecker] = useState("")
  if (node.config !== undefined){
    try {
      var original_img = require( `../../data/${node.config}activity_screenshots/${node.activity}/${node.nodeName}.png`);
      var cam_gb_img = require( `../../data/${node.config}ui_issue_cam/${node.activity}/${node.nodeName}/cam_gb.jpg`);
      var cam_img = require( `../../data/${node.config}ui_issue_cam/${node.activity}/${node.nodeName}/cam.jpg`);
      var gb_img = require( `../../data/${node.config}ui_issue_cam/${node.activity}/${node.nodeName}/gb.jpg`);
    } catch (error) {

    }

    var issues = true;
    try {
      var google_scanner_img = require( `../../data/${node.config}issues/${node.activity}/${node.nodeName}.png`);
      var text_data = require( `../../data/${node.config}issues/${node.activity}/${node.nodeName}.txt`);
    } catch (error) {
      issues = false;
    }

    if (issues) {
      fetch(text_data)
        .then((r) => r.text())
        .then(text  => {
          setData(text);
        }) 
    }
    
    var crash = true
    try {
      var text = require(`../../data/${node.config}crash_record.json`);
    } catch (error) {
      crash = false
    }
   }

  return (
    <div style={{width: "100%", paddingTop: "15px"}} className="detail-page">
        <h2 className="d-flex justify-content-between" style={{fontWeight: "bold"}}> Original Image</h2>
        <Row>
          <Col>
            <img src={original_img} style={{width: '30%'}} alt = "original img"/>
          </Col>
        </Row>
        <h2 className="d-flex justify-content-between" style={{fontWeight: "bold"}}> Visual Issues</h2>
        <Row>
        <Col><img src= {cam_img} style= {{width: '100%'}} alt = "cam scanner img"/></Col>
        <Col><img src= {cam_gb_img} style= {{width: '100%'}} alt = "cam gb scanner img"/></Col>
        <Col><img src= {gb_img} style= {{width: '100%'}} alt = "gb scanner img"/></Col>
        </Row>
        <br/> 
        <h2 className="d-flex justify-content-between" style={{fontWeight: "bold"}}> Google Accessibility Scanner Report</h2>
        {issues ? <div> 
        <img src= {google_scanner_img} style= {{width: '15vw', paddingBottom:10}} alt = "google scanner img"/>
        <pre style={{'text-align': 'left', 'backgroundColor': 'white', width: '97%', height: '50vh'}}>{google_report}</pre>
        </div> : <p>No issues found</p>}
        <br />
        <h2 className="d-flex justify-content-between" style={{fontWeight: "bold"}}> Crash Record</h2>
        {crash ? <div><pre style={{'text-align': 'left', 'backgroundColor': 'white', width: '98%'}}>{JSON.stringify(text, null, 2) }</pre></div> : <p>No crash record found</p>}
    </div>
  )
}

export default DetailPage 