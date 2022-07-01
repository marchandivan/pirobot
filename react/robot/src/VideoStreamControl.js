import Grid from "@material-ui/core/Grid";
import Stack from '@mui/material/Stack';
import IconButton from "@material-ui/core/IconButton";
import DownloadIcon from '@mui/icons-material/Download';
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import PictureInPictureIcon from '@mui/icons-material/PictureInPicture';
import SwitchCameraIcon from '@mui/icons-material/SwitchCamera';
import React from "react";

class LightControl extends React.Component {

    render() {
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <img
                        src={(process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL : "") + "/api/stream/"}
                        width="95%"
                        height="95%"
                        alt="Camera Feed"
                        onMouseMove={this.props.onMouseMove}
                        onClick={this.props.onClick}
                    />
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                  <Stack spacing={0} direction="row" alignItems="center" justifyContent="center">
                    <IconButton onClick={this.props.capture_image_callback.bind(this, "lcd", this.props.selected_camera)}><CameraAltIcon/></IconButton>
                    <IconButton onClick={this.props.capture_image_callback.bind(this, "download", this.props.selected_camera)}><DownloadIcon/></IconButton>
                    <IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera === "front" ? "arm" : "front", this.props.overlay)}><SwitchCameraIcon/></IconButton>
                    <IconButton onClick={this.props.stream_setup_callback.bind(this, this.props.selected_camera, !this.props.overlay)}><PictureInPictureIcon/></IconButton>
                  </Stack>
                </Grid>
            </Grid>
        )
    }
}

export default LightControl;
