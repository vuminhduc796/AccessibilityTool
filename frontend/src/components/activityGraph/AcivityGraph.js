import React from 'react'
import { useState } from "react";
import { useEffect } from 'react';
import { useCallback } from 'react';
import { useContext } from 'react';
import { useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import "./activityGraph.css"
import "bootstrap/dist/css/bootstrap.min.css";
import { useWindowSize } from '@react-hook/window-size';
import { AppContext } from '../../context/Context';

const AcivityGraph = React.memo(()  => {

    var newData = {nodes: [], links: []};
    var data = useContext(AppContext);
    var [currentNode, setNode] = data["currentNode"]
    var [gData, setData] = data["gData"]
    var [currentConfig,setCurrentConfig] = data["currentConfig"]
    var [configs,setConfigs] = data["configs"]

    const [cacheData, setCacheData] =  useState({});
    const [cacheConfigs, setCacheConfigs] =  useState({});
    const [directory, setDirectory] =  useState("");

    const graphRef = useRef();

    const tryLoadData = () => {
      try {
       return require("../../data/config.json");
      } catch (err) {
       return null;
      }
    };

    useEffect(() => {
      
      const interval = setInterval(() => {

           
        
        var readData = tryLoadData()

        if (readData !== null){

          var dataConfigs = readData.configs;     

          if (dataConfigs !== cacheData || cacheConfigs !== currentConfig){


            setConfigs(dataConfigs)
          // use config to get directory
          var isFound = false;
          for(var currentConfigIndex = 0; currentConfigIndex < dataConfigs.length; currentConfigIndex ++){
            var dataConfig = dataConfigs[currentConfigIndex]
              if (dataConfig.config.device === currentConfig.device && dataConfig.config.mode ===  currentConfig.mode && dataConfig.config.appName === currentConfig.appName){
                isFound = true
                loadDataForGraph(dataConfig)
              }

            }
            setCacheData(dataConfigs);
            setCacheConfigs(currentConfig);
          }
        }
      }, 2000);
    
      return () => clearInterval(interval);
    }, [gData,directory,currentConfig,cacheConfigs,cacheData]);

    const loadDataForGraph = dataConfig => {
      var folderPath = dataConfig.config.appName + "/" + dataConfig.config.device + "/" + dataConfig.config.mode + "/" ;
      setDirectory(folderPath);

      var sources = []
      for (var i=0; i<dataConfig.config.edges.length; i++) {
        var link = dataConfig.config.edges[i]
        if (link.source && link.destination) {
          newData.links.push(
            {
              "target":link.destination,
              "source":link.source
            }
          )
        }
        else {
          sources.push(link.destination)
        }
      }

      // set data for node
        
        var currentID = 0;
        for (var i = 0; i < dataConfig.config.activities.length; i++){
          var activityName = dataConfig.config.activities[i];
          for (var j = 0; j < dataConfig.config.nodes.length; j++) {
            var nodeName = dataConfig.config.nodes[j];
            if (nodeName.includes(activityName)) {
              var newNode = {
                id: nodeName,
                img: activityName + "/" + nodeName + ".jpg",
                activity: activityName,
                activityId: i,
                nodeName: nodeName,
                config: folderPath,
                source: sources.includes(nodeName)
              };
              if (currentID === 0) {
                setNode(newNode);
              }
              
              newData.nodes.push(newNode);
              currentID ++;
            }
          }
        }
        setData(newData);
    }
    const [width, height] = useWindowSize();

    const tickFunc = (ref) => {
      try {
        ref.d3Force('center').strength(0)
        ref.d3Force('charge').strength(-60)
        //ref.d3Force('link').distance(400)
        ref.d3Force('link').strength(-0.01)
      }
      catch(err) {

      }
    }

    function getUniqueColor(n) {
      const rgb = [0, 0, 0];
  
      for (let i = 0; i < 24; i++) {
          rgb[i%3] <<= 1;
          rgb[i%3] |= n & 0x01;
          n >>= 1;
      }
  
      return '#' + rgb.reduce((a, c) => (c > 0x0f ? c.toString(16) : '0' + c.toString(16)) + a, '');
  }

  return (
    <div >
<ForceGraph2D
      ref={graphRef}
      graphData={gData}
      maxZoom = {20}
      forceEngine="d3"
      
      nodeCanvasObject={(node, ctx, globalScale) => { 
        var img = new Image(); 
        const activityColors = ["red", "green", "blue", "purple", "orange", "pink"]
        try {
          img.src = require( `../../data/${directory}activity_screenshots/${node.img}`)
        } catch (error) {
          
        }
        

        if(node.activity === currentNode.activity) {
          ctx.beginPath();
          ctx.fillStyle = "#fffb03";
          ctx.fillRect(node.x - 34, node.y - 69, 79, 139);
          ctx.stroke();
        }
        else{
          ctx.beginPath();
          ctx.fillStyle = getUniqueColor(node.activityId);
          ctx.fillRect(node.x - 34, node.y - 69, 79, 139);
          ctx.stroke();
        }
        var x=node.x;var y=node.y;

        ctx.drawImage(img, node.x - 32, node.y - 67, 75, 135);

        if (node.source) {
          var entry_img = new Image();
          entry_img.src = require(`../../images/entry.png`)  
          ctx.drawImage(entry_img, node.x-40, node.y-65, 40, 35)
        }

        if (node.nodeName === currentNode.nodeName) {
          var eye_img = new Image();
          eye_img.src = require(`../../images/eye.png`);
          ctx.drawImage(eye_img, node.x-20, node.y-18, 50, 30);
        }
        }}

        d3AlphaMin={0.01}
        onEngineTick={tickFunc(graphRef.current)}
        linkDirectionalArrowLength={20}
        linkDirectionalArrowRelPos={0.5}
        linkDirectionalArrowColor={() => "black"}
        linkCurvature={0.25} 
        linkWidth={5}
        height= {height * 0.92}
        width= {width/1.7} 
        onNodeClick={ node => {setNode(node)}}
        onNodeDragEnd={node => {
          node.fx = node.x;
          node.fy = node.y;
          node.fz = node.z;
        }}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.fillStyle = color;
          ctx.fillRect(node.x - 32, node.y - 67, 96, 135);
        }}
        />
    </div>

   
  )
});

function drawArrow(ctx, fromx, fromy, tox, toy, arrowWidth, color){
  //variables to be used when creating the arrow
  var headlen = 2;
  var angle = Math.atan2(toy-fromy,tox-fromx);

  ctx.save();
  ctx.strokeStyle = color;

  //starting path of the arrow from the start square to the end square
  //and drawing the stroke
  ctx.beginPath();
  ctx.moveTo(fromx, fromy);
  ctx.lineTo(tox, toy);
  ctx.lineWidth = arrowWidth;
  ctx.stroke();

  //starting a new path from the head of the arrow to one of the sides of
  //the point
  ctx.beginPath();
  ctx.moveTo(tox, toy);
  ctx.lineTo(tox-headlen*Math.cos(angle-Math.PI/7),
             toy-headlen*Math.sin(angle-Math.PI/7));

  //path from the side point of the arrow, to the other side point
  ctx.lineTo(tox-headlen*Math.cos(angle+Math.PI/7),
             toy-headlen*Math.sin(angle+Math.PI/7));

  //path from the side point back to the tip of the arrow, and then
  //again to the opposite side point
  ctx.lineTo(tox, toy);
  ctx.lineTo(tox-headlen*Math.cos(angle-Math.PI/7),
             toy-headlen*Math.sin(angle-Math.PI/7));

  //draws the paths created above
  ctx.stroke();
  ctx.restore();
}

export default AcivityGraph