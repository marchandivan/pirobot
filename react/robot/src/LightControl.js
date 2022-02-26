import Grid from '@material-ui/core/Grid';
import React from 'react';
import Stack from '@mui/material/Stack';
import IconButton from "@material-ui/core/IconButton";
import FlashlightOnIcon from '@mui/icons-material/FlashlightOn';
import FlashlightOffIcon from '@mui/icons-material/FlashlightOff';

class LightControl extends React.Component {

    render() {
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p>Lights</p>
                </Grid>
                <Grid container>
                    <Grid item xl={1} md={1} sm={1} xs={1}/>
                    <Grid item xl={4} md={4} sm={4} xs={4}>
                        <p style={{fontSize: 16}}>Front</p>
                    </Grid>
                    <Grid item xl={6} md={6} sm={6} xs={6}>
                        <Stack spacing={0} direction="row" alignItems="center" justifyContent="center">
                            <IconButton onClick={this.props.set_light_callback.bind(this, false, false, this.props.arm_on)}><FlashlightOffIcon/></IconButton>
                            <IconButton onClick={this.props.set_light_callback.bind(this, true, true, this.props.arm_on)}><FlashlightOnIcon/></IconButton>
                        </Stack>
                    </Grid>
                    <Grid item xl={1} md={1} sm={1} xs={1}/>
                    <Grid item xl={1} md={1} sm={1} xs={1}/>
                    <Grid item xl={4} md={4} sm={4} xs={4}>
                        <p style={{fontSize: 16}}>Arm</p>
                    </Grid>
                    <Grid item xl={6} md={6} sm={6} xs={6}>
                        <Stack spacing={0} direction="row" alignItems="center" justifyContent="center">
                            <IconButton onClick={this.props.set_light_callback.bind(this, this.props.left_on, this.props.right_on, false)}><FlashlightOffIcon/></IconButton>
                            <IconButton onClick={this.props.set_light_callback.bind(this, this.props.left_on, this.props.right_on, true)}><FlashlightOnIcon/></IconButton>
                        </Stack>
                    </Grid>
                    <Grid item xl={1} md={1} sm={1} xs={1}/>
                </Grid>
            </Grid>
        )
    }
}

export default LightControl;
