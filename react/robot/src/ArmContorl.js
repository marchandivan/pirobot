import Grid from '@material-ui/core/Grid';
import React from 'react';
import Button from '@material-ui/core/Button';
import Slider from '@material-ui/core/Slider';
import Stack from '@mui/material/Stack';
import ThreeSixtyIcon from '@mui/icons-material/ThreeSixty';
import ReplayIcon from '@mui/icons-material/Replay';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import CloseFullscreenIcon from '@mui/icons-material/CloseFullscreen';
import OpenInFullIcon from '@mui/icons-material/OpenInFull';
import IconButton from "@material-ui/core/IconButton";

class ArmControl extends React.Component {

    render() {
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p>
                        Arm Controls
                    </p>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={1} direction="row" alignItems="center">
                        <PrecisionManufacturingIcon/>
                        <IconButton onClick={this.props.open_claw_callback}><OpenInFullIcon/></IconButton>
                        <Slider
                            value={this.props.position_claw}
                            min={0}
                            max={90}
                            step={1}
                            onChange={this.props.move_claw_callback}
                            aria-label="Claw Angle"/>
                        <IconButton onClick={this.props.close_claw_callback}><CloseFullscreenIcon/></IconButton>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={1} direction="row" alignItems="center">
                        <ReplayIcon/>
                        <Slider
                            value={this.props.position_wrist}
                            min={0}
                            max={this.props.max_angle_wrist}
                            step={1}
                            onChange={this.props.move_wrist_callback}
                            aria-label="Speed Slider"/>
                        <p style={{fontSize: 16}}>{this.props.position_wrist}°</p>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={1} direction="row" alignItems="center">
                        <ReplayIcon/>
                        <Slider
                            value={this.props.position_forearm}
                            min={0}
                            max={this.props.max_angle_forearm}
                            step={1}
                            onChange={this.props.move_forearm_callback}
                            aria-label="Speed Slider"/>
                        <p style={{fontSize: 16}}>{this.props.position_forearm}°</p>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <Stack spacing={1} direction="row" alignItems="center">
                        <ThreeSixtyIcon/>
                        <Slider
                            value={this.props.position_shoulder}
                            min={0}
                            max={this.props.max_angle_shoulder}
                            step={1}
                            onChange={this.props.move_shoulder_callback}
                            aria-label="Speed Slider"/>
                        <p style={{fontSize: 16}}>{this.props.position_shoulder}°</p>
                    </Stack>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p style={{fontSize: 16}}>Preset</p>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "left_camera")}>Left</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "backup_camera")}>Back</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "right_camera")}>Right</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "pickup")}>Pick</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "grap")}>Grab</Button>
                </Grid>
                <Grid item xl={4} md={4} sm={4} xs={4}>
                    <Button style={{fontSize: 10}} variant="contained" onClick={this.props.move_to_position_callback.bind(this, "drop")}>Drop</Button>
                </Grid>
            </Grid>
        )
    }
}

export default ArmControl;
