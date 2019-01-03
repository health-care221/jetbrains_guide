import { Link } from 'gatsby';
import * as React from 'react';
import { INavbarMenuItemProps } from './NavbarMenuItem';
import { INavbarSubMenuProps } from './NavbarSubMenu';

export interface INavbarStartProps {
  items: INavbarMenuItemProps[] | INavbarSubMenuProps[];
}

const NavbarStart: React.FunctionComponent<INavbarStartProps> = () => (
  <div className="navbar-start">
    <Link className={'navbar-item bd-navbar-item-documentation'} to={`/tips`}>
      <span className={'icon has-text-success'}>
        <i className={'fas fa-play-circle'} />
      </span>
      <span className="bulmaio-menu-label">Tips</span>
    </Link>

    <Link className={'navbar-item bd-navbar-item-documentation'} to={`/technologies`}>
      <span className={'icon has-text-danger'}>
        <i className={'fas fa-project-diagram'} />
      </span>
      <span className="bulmaio-menu-label">Technologies</span>
    </Link>

    <Link className={'navbar-item bd-navbar-item-documentation'} to={`/topics`}>
      <span className={'icon has-text-primary'}>
        <i className={'fas fa-project-diagram'} />
      </span>
      <span className="bulmaio-menu-label">Topics</span>
    </Link>

    <Link className={'navbar-item bd-navbar-item-documentation'} to={`/authors`}>
      <span className={'icon has-text-info'}>
        <i className={'fas fa-users'} />
      </span>
      <span className="bulmaio-menu-label">Authors</span>
    </Link>

    <div className="navbar-item has-dropdown is-hoverable">
      <span className="navbar-link bio-dropdown-main">More</span>
      <div id="moreDropdown" className="navbar-dropdown">
        <Link className="navbar-item " to={`/about`}>
          <span>
            <span className={'icon has-text-success'}>
              <i className={'fas fa-rocket'} />
            </span>
            <strong>About the Guide</strong>
            <br />
            <span className="bio-dropdown-description">Community-driven compendium of PyCharm learning resources</span>
          </span>
        </Link>
      </div>
    </div>
  </div>
);

export default NavbarStart;
