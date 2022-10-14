import Grid from "@material-ui/core/Grid";
import Slider from '@material-ui/core/Slider';
import Stack from '@mui/material/Stack';
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import DangerousIcon from '@mui/icons-material/Dangerous';
import DownloadIcon from '@mui/icons-material/Download';
import FaceIcon from '@mui/icons-material/Face';
import IconButton from "@material-ui/core/IconButton";
import FaceRetouchingOffIcon from '@mui/icons-material/FaceRetouchingOff';
import Tooltip from "@material-ui/core/Tooltip";
import PictureInPictureIcon from '@mui/icons-material/PictureInPicture';
import SwitchCameraIcon from '@mui/icons-material/SwitchCamera';
import VerticalAlignCenterIcon from '@mui/icons-material/VerticalAlignCenter';
import RadarIcon from '@mui/icons-material/Radar';
import React from "react";

class LightControl extends React.Component {

    render() {
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack
                        spacing={0}
                        justifyContent="center"
                        alignItems="center"
                        direction="row">
                    <img
                        src={(process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL : "") + "/api/stream/"}
                        style={{maxHeight: window.outerHeight * 0.7}}
                        width={window.outerWidth > window.outerHeight ? window.outerWidth * 0.63 : window.outerWidth * 0.9}
                        alt="Camera Feed"
                        onMouseMove={this.props.onMouseMove}
                        onClick={this.props.onClick}
                    />
                    <Stack
                        sx={{ height: 500 }}
                        justifyContent="center"
                        alignItems="center"
                        direction="column">
                        <Slider
                            min={0}
                            max={100}
                            step={1}
                            aria-label="Camera position"
                            orientation="vertical"
                            valueLabelDisplay="auto"
                            value={this.props.camera_position}
                            onChange={this.props.set_camera_position}
                            marks={[{value: this.props.center_position}]}
                        />
                        <IconButton onClick={this.props.centerCameraPosition}><VerticalAlignCenterIcon/></IconButton>
                    </Stack>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                  <Stack spacing={0} direction="row" alignItems="center" justifyContent="center">
                    {this.props.robot_has_screen && (<IconButton onClick={this.props.capture_image_callback.bind(this, "lcd", this.props.selected_camera)}><CameraAltIcon/></IconButton>)}
                    <Tooltip title="Snapshot"><IconButton onClick={this.props.capture_image_callback.bind(this, "download", this.props.selected_camera)}><DownloadIcon/></IconButton></Tooltip>
                    {this.props.robot_has_back_camera && (<IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera === "front" ? "arm" : "front", this.props.overlay, this.props.face_detection)}><SwitchCameraIcon/></IconButton>)}
                    {this.props.robot_has_back_camera && (<IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera, !this.props.overlay, this.props.face_detection)}><PictureInPictureIcon/></IconButton>)}
                    <Tooltip title="Face Recognition"><IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera, this.props.overlay, !this.props.face_detection)}>{this.props.face_detection ? (<FaceRetouchingOffIcon/>):(<FaceIcon/>)}</IconButton></Tooltip>
                    <Tooltip title="Start Patrolling"><IconButton onClick={this.props.patrol}><RadarIcon/></IconButton></Tooltip>
                    <Tooltip title="Stop Robot"><IconButton alt="Stop Robot" onClick={this.props.stopRobot}><DangerousIcon alt="Stop Robot"/></IconButton></Tooltip>
                  </Stack>
                </Grid>
            </Grid>
        )
    }
}

export default LightControl;
