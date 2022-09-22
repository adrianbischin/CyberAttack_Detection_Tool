import React, { Component } from "react"
import './VisualiseBookings.css'
import "../../commons/css/w3.css"
import 'font-awesome/css/font-awesome.css'
import axios from 'axios'
import swal from 'sweetalert'
import { DropdownButton } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'

export default class VisualiseBookings extends Component {

    constructor(props) {
        super(props)

        this.renderTableHeaderBookings = this.renderTableHeaderBookings.bind(this);
        this.renderTableDataBookings = this.renderTableDataBookings.bind(this);

        this.state = {
            bookings: [],
            name: this.props.match.params.name
        }
    }

    componentDidMount() {
        console.log(this.state.name)
        let visits = {
            name: this.state.name
        }
        axios.get('/sanctum/csrf-cookie').then(response => {
            axios.post('/api/getVisitsForLocation', visits).then(res => {
                this.setState({ bookings: res.data.bookings });
            });
        });
    }

    renderTableHeaderBookings() {
        let headerElement = ['User', 'Date', 'Hour']

        return headerElement.map((key, index) => {
            return <th key={index}>{key.toUpperCase()}</th>
        })
    }

    renderTableDataBookings() {

        return this.state.bookings.map(locatie => {
            const { id, user, date, hour } = locatie //destructuring
            return (
                <tr key={id}>
                    <td >{user}</td>
                    <td>{date}</td>
                    <td>{hour+":00-"+(hour+1)+":00"}</td>
                </tr>
            )
        })

    }

    render() {

        return (
            <div>
                <h1 align={'center'} style={{ marginTop: "3%", fontWeight: "bold", color: "white", textShadow: "3px 3px #000000", textDecoration:"underline" }}>Visualise Bookings for {this.state.name}:</h1>
            
                <table id='locations' style={{ width: '80%', marginLeft: '10%', marginTop: '3%' }}>
                    <tbody>
                        <tr>{this.renderTableHeaderBookings()}</tr>
                        {this.renderTableDataBookings()}
                    </tbody>
                </table>
            </div>


        );
    }
}
