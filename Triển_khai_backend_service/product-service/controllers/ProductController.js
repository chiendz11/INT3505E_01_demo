/**
 * The ProductController file is a very simple one, which does not need to be changed manually,
 * unless there's a case where business logic routes the request to an entity which is not
 * the service.
 * The heavy lifting of the Controller item is done in Request.js - that is where request
 * parameters are extracted and sent to the service, and where response is handled.
 */

const Controller = require('./Controller');
const service = require('../services/ProductService');
const productsGET = async (request, response) => {
  await Controller.handleRequest(request, response, service.productsGET);
};

const productsIdDELETE = async (request, response) => {
  await Controller.handleRequest(request, response, service.productsIdDELETE);
};

const productsIdGET = async (request, response) => {
  await Controller.handleRequest(request, response, service.productsIdGET);
};

const productsIdPUT = async (request, response) => {
  await Controller.handleRequest(request, response, service.productsIdPUT);
};

const productsPOST = async (request, response) => {
  await Controller.handleRequest(request, response, service.productsPOST);
};


module.exports = {
  productsGET,
  productsIdDELETE,
  productsIdGET,
  productsIdPUT,
  productsPOST,
};
