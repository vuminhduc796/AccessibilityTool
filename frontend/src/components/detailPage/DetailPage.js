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
    

    //var google_scanner_img = require( `/data/domain/phone-vertical/normal_light_mode/googleScanner/issues/au.com.domain.feature.home.HomeActivity/au.com.domain.feature.home.HomeActivity.png`);
    //var text_data = require( `/Users/vuminhduc796/Desktop/Research/Research Platform/accessibility-tool/src/data/domain/phone-vertical/normal_light_mode/googleScanner/issues/au.com.domain.feature.home.HomeActivity/au.com.domain.feature.home.HomeActivity.txt`);

  //   fetch(text_data)
  //       .then((r) => r.text())
  //       .then(text  => {
  //         setData(text);
  //       }) 
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
        <Row> 
        {/* <img src= {google_scanner_img} style= {{width: '33%'}} alt = "google scanner img"/> */}
        <Col><textarea style= {{width: '90%', height: '150px'}} defaultValue={google_report} readOnly={true}></textarea></Col>
        </Row>
        <br />
        {crash ? <div><h2 className="d-flex justify-content-between" style={{fontWeight: "bold"}}> Crash Record</h2>
          <pre style={{'text-align': 'left', 'background-color': 'white', width: '98%'}}>{JSON.stringify(text, null, 2) }</pre></div> : ''}
    </div>
  )
}

export default DetailPage 