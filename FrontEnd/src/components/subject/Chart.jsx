"use client";
import React, { useState, useEffect } from "react";
import styles from "./chart.module.css";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function BarChart({ graphData }) {
  const isWindowAvailable = typeof window !== "undefined";
  const [viewportWidth, setViewportWidth] = useState(
    isWindowAvailable ? window.innerWidth : null
  );

  const chartOrientation = viewportWidth < 600 ? "horizontalBar" : "bar";

  useEffect(() => {
    if (isWindowAvailable) {
      function handleResize() {
        setViewportWidth(window.innerWidth);
      }

      window.addEventListener("resize", handleResize);
      return () => window.removeEventListener("resize", handleResize);
    }
  }, [isWindowAvailable]);

  const colors = [
    "rgba(0, 64, 193, 1)",
    "rgba(5, 145, 248, 1)",
    "rgba(39, 223, 243, 1)",
    "rgba(117, 220, 159, 1)",
    "rgba(0, 169, 165, 1)",
  ];

  const characteristics = [
    ["overall", "Total"],
    ["clarity", "Claritate"],
    ["comprehension", "Înțelegere"],
    ["interactivity", "Interactivitate"],
    ["relevance", "Relevanță"],
  ];

  const characteristicData = {};
  characteristics.forEach((characteristic) => {
    characteristicData[characteristic[0]] = Object.keys(graphData).map(
      (week) => graphData[week][characteristic[0]]
    );
  });

  const options = {
    indexAxis: chartOrientation === "horizontalBar" ? "y" : "x",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        onClick: () => {},
      },
    },
    scales: {
      x: {
        ticks: {
          stepSize: 1,
        },
        beginAtZero: true,
        suggestedMax: 5,
        title: {
          display: true,
          text: "Săptămâna",
          font: {
            size: 14,
          },
        },
      },
      y: {
        title: {
          display: true,
          text: "Media",
          font: {
            size: 14,
          },
        },
        ticks: {
          stepSize: 1,
        },
        beginAtZero: true,
        suggestedMax: 5,
      },
    },
  };
  const axisLabels =
    chartOrientation === "horizontalBar"
      ? ["Media", "Săptămâna"]
      : ["Săptămâna", "Media"];
  options.scales.x.title.text = axisLabels[0];
  options.scales.y.title.text = axisLabels[1];

  const labels = [];
  for (let i = 1; i <= 14; i++) {
    labels.push(`S${i}`);
  }

  const [selectedDataset, setSelectedDataset] = useState("Total");

  const handleDatasetChange = (event) => {
    setSelectedDataset(event.target.value);
  };

  const datasets = characteristics.map((characteristic, index) => ({
    label: characteristic[1],
    data: characteristicData[characteristic[0]],
    backgroundColor: colors[index],
  }));

  console.log(datasets);

  const selectedData = datasets.find(
    (dataset) => dataset.label === selectedDataset
  );

  return (
    <>
      <Bar
        options={options}
        data={{ labels, datasets: [selectedData] }}
        width="600"
        height="250"
      />
      <div className={styles.selectContainer}>
        <select value={selectedDataset} onChange={handleDatasetChange}>
          {characteristics.map((characteristic, index) => (
            <option key={index} value={characteristic[1]}>
              {characteristic[1]}
            </option>
          ))}
        </select>
      </div>
    </>
  );
}
